module PC(
    input  logic clk, 
    input  logic reset, 
    input  logic [31:0] next_pc, 
    output logic [31:0] pc
);
    always_ff @(posedge clk or posedge reset) begin
        if (reset)
            pc <= 32'h00000000;
        else
            pc <= next_pc;
    end
endmodule

module ImmGen(
    input  logic [31:0] inst, 
    output logic [31:0] imm32
);
    always_comb begin
        case (inst[6:0])
            7'h13: imm32 = {{20{inst[31]}}, inst[31:20]};           // Tipo I (addi, etc)
            7'h03: imm32 = {{20{inst[31]}}, inst[31:20]};           // Tipo I (load)
            7'h23: imm32 = {{20{inst[31]}}, inst[31:25], inst[11:7]}; // Tipo S (sw)
            7'h63: imm32 = {{19{inst[31]}}, inst[31], inst[7], inst[30:25], inst[11:8], 1'b0}; // Tipo B
            7'h37: imm32 = {inst[31:12], 12'b0};                    // Tipo U (lui)
            7'h6F: imm32 = {{11{inst[31]}}, inst[31], inst[19:12], inst[20], inst[30:21], 1'b0}; // Tipo J
            default: imm32 = 32'b0;
        endcase
    end
endmodule

module RegisterFile(
    input  logic clk, 
    input  logic regWrite, 
    input  logic [4:0] rs1, 
    input  logic [4:0] rs2, 
    input  logic [4:0] rd, 
    input  logic [31:0] writeData, 
    output logic [31:0] readData1, 
    output logic [31:0] readData2
);
    logic [31:0] registers [31:0];

    // Lectura asíncrona combinacional
    assign readData1 = (rs1 == 5'b0) ? 32'b0 : registers[rs1];
    assign readData2 = (rs2 == 5'b0) ? 32'b0 : registers[rs2];

    // Escritura síncrona
    always_ff @(posedge clk) begin
        if (regWrite && rd != 5'b0)
            registers[rd] <= writeData;
    end
endmodule

module ALU(
    input  logic [31:0] A, 
    input  logic [31:0] B, 
    input  logic [3:0] aluControl, 
    output logic [31:0] result, 
    output logic zero
);
    always_comb begin
        case (aluControl)
            4'b0000: result = A + B;       // Sumar
            4'b0001: result = A - B;       // Restar
            4'b0010: result = A & B;       // AND
            4'b0011: result = A | B;       // OR
            4'b0100: result = A ^ B;       // XOR
            4'b0101: result = A << B[4:0]; // SLL
            4'b0110: result = A >> B[4:0]; // SRL
            4'b0111: result = $signed(A) >>> B[4:0]; // SRA
            default: result = 32'b0;
        endcase
    end

    assign zero = (result == 32'b0);
endmodule

module ControlUnit(
    input  logic [6:0] opcode, 
    output logic branch, memRead, memToReg, memWrite, aluSrc, regWrite, jump,
    output logic [1:0] aluOp
);
    always_comb begin
        // Valores por defecto
        branch = 0; memRead = 0; memToReg = 0; aluOp = 2'b00; 
        memWrite = 0; aluSrc = 0; regWrite = 0; jump = 0;

        case (opcode)
            7'h33: begin regWrite = 1; aluOp = 2'b10; end // Tipo R
            7'h13: begin regWrite = 1; aluSrc = 1; aluOp = 2'b10; end // Tipo I
            7'h03: begin regWrite = 1; aluSrc = 1; memRead = 1; memToReg = 1; end // lw
            7'h23: begin aluSrc = 1; memWrite = 1; end // sw
            7'h63: begin branch = 1; aluOp = 2'b01; end // branch
            7'h6F: begin regWrite = 1; jump = 1; end // jal
            default: ; 
        endcase
    end
endmodule

module ALUControl(
    input  logic [1:0] aluOp, 
    input  logic [2:0] funct3, 
    input  logic [6:0] funct7, 
    output logic [3:0] aluControl
);
    always_comb begin
        case (aluOp)
            2'b00: aluControl = 4'b0000; // Suma (Loads/Stores)
            2'b01: aluControl = 4'b0001; // Resta (Branches)
            2'b10: begin // Tipo R o I
                case (funct3)
                    3'h0: aluControl = (funct7[5]) ? 4'b0001 : 4'b0000;
                    3'h7: aluControl = 4'b0010;
                    3'h6: aluControl = 4'b0011;
                    3'h4: aluControl = 4'b0100;
                    3'h1: aluControl = 4'b0101;
                    3'h5: aluControl = (funct7[5]) ? 4'b0111 : 4'b0110;
                    default: aluControl = 4'b0000;
                endcase
            end
            default: aluControl = 4'b0000;
        endcase
    end
endmodule

module DataMemory(
    input  logic clk,
    input  logic memWrite,
    input  logic memRead,
    input  logic [31:0] address,
    input  logic [31:0] writeData,
    output logic [31:0] readData
);
    logic [31:0] ram [0:255];

    always_ff @(posedge clk) begin
        if (memWrite)
            ram[address >> 2] <= writeData;
    end

    assign readData = memRead ? ram[address >> 2] : 32'b0;
endmodule

module RISCV_Core(
    input logic clk, 
    input logic reset
);
    // Cables internos con SystemVerilog 'logic'
    logic [31:0] pc, next_pc, inst, imm32, readData1, readData2, aluResult, writeData, readMemData;
    logic [3:0]  aluControl;
    logic [1:0]  aluOp;
    logic regWrite, aluSrc, memRead, memWrite, memToReg, branch, zero, jump;
    
    // --- Lógica del PC y Saltos ---
    logic is_beq, is_bne, take_branch;
    assign is_beq = (inst[14:12] == 3'b000); // 000 para BEQ
    assign is_bne = (inst[14:12] == 3'b001); // 001 para BNE
    assign take_branch = branch && ((is_beq && zero) || (is_bne && !zero));
    
    assign next_pc = (jump || take_branch) ? (pc + imm32) : (pc + 4);
    
    PC pc_unit(clk, reset, next_pc, pc);

    // --- Memoria de Instrucciones (ROM) ---
    logic [31:0] rom [0:255]; 

    initial begin
        rom[0] = 32'h00a00293; // addi x5, x0, 10
        rom[1] = 32'h01400313; // addi x6, x0, 20
        rom[2] = 32'h006283b3; // add  x7, x5, x6
        rom[3] = 32'h00239393; // slli x7, x7, 2
        rom[4] = 32'h00512423; // sw   x5, 8(x2)
        rom[5] = 32'h00002503; // lw   x10, 0(x0)
        rom[6] = 32'h7cb51863; // bne  x10, x11, 2000
    end
    
    assign inst = rom[pc >> 2];

    // --- Instancias de Módulos ---
    ControlUnit  ctrl(inst[6:0], branch, memRead, memToReg, aluOp, memWrite, aluSrc, regWrite, jump);
    ImmGen       igen(inst, imm32);
    RegisterFile regs(clk, regWrite, inst[19:15], inst[24:20], inst[11:7], writeData, readData1, readData2);
    ALUControl   actrl(aluOp, inst[14:12], inst[31:25], aluControl);
    
    // Mux de la ALU
    logic [31:0] alu_in_b;
    assign alu_in_b = aluSrc ? imm32 : readData2;
    
    ALU alu_unit(readData1, alu_in_b, aluControl, aluResult, zero);

    // Nuestra NUEVA instancia de la Memoria de Datos
    DataMemory ram_unit(clk, memWrite, memRead, aluResult, readData2, readMemData);

    // Mux para decidir qué escribir en el registro
    assign writeData = memToReg ? readMemData : aluResult;

endmodule