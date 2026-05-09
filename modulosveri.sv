// ============================================================================
// MODULOS AUXILIARES
// ============================================================================

module decodificador_7seg(
    input  logic [3:0] binario,
    output logic [6:0] segmentos
);
    always_comb begin
        case (binario)
            4'h0: segmentos = 7'b1000000;
            4'h1: segmentos = 7'b1111001;
            4'h2: segmentos = 7'b0100100;
            4'h3: segmentos = 7'b0110000;
            4'h4: segmentos = 7'b0011001;
            4'h5: segmentos = 7'b0010010;
            4'h6: segmentos = 7'b0000010;
            4'h7: segmentos = 7'b1111000;
            4'h8: segmentos = 7'b0000000;
            4'h9: segmentos = 7'b0010000;
            4'hA: segmentos = 7'b0001000;
            4'hB: segmentos = 7'b0000011;
            4'hC: segmentos = 7'b1000110;
            4'hD: segmentos = 7'b0100001;
            4'hE: segmentos = 7'b0000110;
            4'hF: segmentos = 7'b0001110;
            default: segmentos = 7'b1111111;
        endcase
    end
endmodule

// ============================================================================
// DATAPATH: PC, Registros, Memoria, ALU
// ============================================================================

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
            7'h13: imm32 = {{20{inst[31]}}, inst[31:20]};           // Tipo I
            7'h03: imm32 = {{20{inst[31]}}, inst[31:20]};           // Tipo I (load)
            7'h23: imm32 = {{20{inst[31]}}, inst[31:25], inst[11:7]}; // Tipo S
            7'h63: imm32 = {{19{inst[31]}}, inst[31], inst[7], inst[30:25], inst[11:8], 1'b0}; // Tipo B
            7'h37: imm32 = {inst[31:12], 12'b0};                    // Tipo U (lui)
            7'h17: imm32 = {inst[31:12], 12'b0};                    // Tipo U (auipc)
            7'h6F: imm32 = {{11{inst[31]}}, inst[31], inst[19:12], inst[20], inst[30:21], 1'b0}; // Tipo J (jal)
            7'h67: imm32 = {{20{inst[31]}}, inst[31:20]};           // Tipo I (jalr)
            default: imm32 = 32'b0;
        endcase
    end
endmodule

module RegisterFile(
    input  logic        regWrite,
    input  logic [4:0]  rs1,
    input  logic [4:0]  rs2,
    input  logic [4:0]  rd,
    input  logic [31:0] writeData,
    output logic [31:0] readData1,
    output logic [31:0] readData2,
    output logic [31:0] debug_a0,
    output logic [1023:0] reg_file_flat
);

    logic [31:0] registers [31:0];
    logic [31:0] next_registers [31:0]; // Array temporal para el próximo estado

     integer i;

    // Inicialización del banco de registros a 0 al encender
    initial begin
        for (int k = 0; k < 32; k++) begin
            registers[k] = 32'b0;
        end
    end

    // Calcula el próximo estado de los registros
    always_comb begin
        for (i = 0; i < 32; i++) begin
            next_registers[i] = registers[i]; // mantiene valor actual
        end
        next_registers[0] = 32'b0;
        if (regWrite && rd != 5'b0)
            next_registers[rd] = writeData;
    end

    // Latches inferidos correctamente por Quartus
    always_comb begin
        for (i = 0; i < 32; i++) begin
            registers[i] = next_registers[i];
        end
    end
      
    assign readData1 = (rs1 == 5'b0) ? 32'b0 : registers[rs1];
    assign readData2 = (rs2 == 5'b0) ? 32'b0 : registers[rs2];
    assign debug_a0  = registers[10];

    genvar j;
    generate
        for (j = 0; j < 32; j++) begin : flatten
            assign reg_file_flat[j*32 +: 32] = registers[j];
        end
    endgenerate

endmodule

module ALU(
    input  logic [31:0] A, 
    input  logic [31:0] B, 
    input  logic [3:0] aluControl, 
    output logic [31:0] result, 
    output logic zero,
    output logic lt,
    output logic ltu
);
    always_comb begin
        case (aluControl)
            4'b0000: result = A + B;
            4'b0001: result = A - B;
            4'b0010: result = A & B;
            4'b0011: result = A | B;
            4'b0100: result = A ^ B;
            4'b0101: result = A << B[4:0];
            4'b0110: result = A >> B[4:0];
            4'b0111: result = $signed(A) >>> B[4:0];
            4'b1000: result = ($signed(A) < $signed(B)) ? 32'b1 : 32'b0;
            4'b1001: result = (A < B) ? 32'b1 : 32'b0;
            4'b1111: result = B; // Pasar B directo (LUI)
            default: result = 32'b0;
        endcase
    end

    assign zero = (result == 32'b0);
    assign lt   = ($signed(A) < $signed(B));
    assign ltu  = (A < B);
endmodule

module DataMemory (
    input  logic        we,         // 1: Escribe (Write), 0: Lee (Read)
    input  logic        isUnsigned, // 1: LBU/LHU, 0: LB/LH
    input  logic [1:0]  size,       // 00: Byte, 01: Half, 10: Word
    input  logic [31:0] address,
    input  logic [31:0] writeData,
    output logic [31:0] readData
);

    // Memoria de 201 bytes (201B)
    logic [7:0] ram [0:200];

    // --- LOGICA ASINCRONA DE ESCRITURA Y LECTURA ---
    always_comb begin
        // Valores por defecto para evitar latches indeseados
        readData = 32'b0;

        if (we) begin
            // --- ESCRITURA ---
            case (size)
                2'b00: begin // SB
                    ram[address]   = writeData[7:0];
                end
                2'b01: begin // SH
                    ram[address]   = writeData[7:0];
                    ram[address+1] = writeData[15:8];
                end
                2'b10: begin // SW
                    ram[address]   = writeData[7:0];
                    ram[address+1] = writeData[15:8];
                    ram[address+2] = writeData[23:16];
                    ram[address+3] = writeData[31:24];
                end
                default: ;
            endcase
        end 
        else begin
            // --- LECTURA ---
            case (size)
                2'b00: begin // LB / LBU
                    if (isUnsigned) 
                        readData = {24'b0, ram[address]};
                    else            
                        readData = {{24{ram[address][7]}}, ram[address]};
                end
                
                2'b01: begin // LH / LHU
                    if (isUnsigned) 
                        readData = {16'b0, ram[address+1], ram[address]};
                    else            
                        readData = {{16{ram[address+1][7]}}, ram[address+1], ram[address]};
                end
                
                2'b10: begin // LW
                    readData = {ram[address+3], ram[address+2], ram[address+1], ram[address]};
                end
                default: ;
            endcase
        end
    end

endmodule

// ============================================================================
// UNIDADES DE CONTROL
// ============================================================================

module ControlUnit(
    input  logic [6:0] opcode, 
    output logic branch, memRead, memToReg, memWrite, aluSrc, regWrite, jump,
    output logic [1:0] aluOp,
    output logic [1:0] jumpType, // 01: JAL, 10: JALR
    output logic ebreak
);
    always_comb begin
        {branch, memRead, memToReg, memWrite, aluSrc, regWrite, jump} = 7'b0;
        aluOp = 2'b00; jumpType = 2'b00; ebreak = 1'b0;

        case (opcode)
            7'h33: begin regWrite = 1; aluOp = 2'b10; end // Tipo R
            7'h13: begin regWrite = 1; aluSrc = 1; aluOp = 2'b10; end // Tipo I
            7'h03: begin regWrite = 1; aluSrc = 1; memRead = 1; memToReg = 1; end // Loads
            7'h23: begin aluSrc = 1; memWrite = 1; end // Stores
            7'h63: begin branch = 1; aluOp = 2'b01; end // Branch
            7'h6F: begin regWrite = 1; jump = 1; jumpType = 2'b01; end // JAL
            7'h67: begin regWrite = 1; jump = 1; jumpType = 2'b10; aluSrc = 1; end // JALR
            7'h37: begin regWrite = 1; aluSrc = 1; aluOp = 2'b11; end // LUI
            7'h17: begin regWrite = 1; aluSrc = 1; aluOp = 2'b00; end // AUIPC
            7'h73: begin ebreak = 1; end // EBREAK - Debugging breakpoint
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
            2'b00: aluControl = 4'b0000; 
            2'b01: aluControl = 4'b0001; 
            2'b10: begin 
                case (funct3)
                    3'h0: aluControl = (funct7[5]) ? 4'b0001 : 4'b0000;
                    3'h1: aluControl = 4'b0101;
                    3'h2: aluControl = 4'b1000;
                    3'h3: aluControl = 4'b1001;
                    3'h4: aluControl = 4'b0100;
                    3'h5: aluControl = (funct7[5]) ? 4'b0111 : 4'b0110;
                    3'h6: aluControl = 4'b0011;
                    3'h7: aluControl = 4'b0010;
                    default: aluControl = 4'b0000;
                endcase
            end
            2'b11: aluControl = 4'b1111; 
            default: aluControl = 4'b0000;
        endcase
    end
endmodule

// ============================================================================
// TOP MODULE (CPU)
// ============================================================================

module RISCV_Core(
    input  logic CLOCK_50,      // Se conserva por compatibilidad con el top-level
    input  logic clk_button,    // Conectar a KEY0
    input  logic reset,         // Conectar a SW0
    input  logic [2:1] SW,      // Conectar SW1 o sw 2 para elegir visualización
    output logic [9:0] LEDR,    // Conectar a LEDR
    output logic [6:0] HEX0,    // Conectar a HEX0
    output logic [6:0] HEX1,	 // Conectar a HEX1
	 output logic [6:0] HEX2,
	 output logic [6:0] HEX3,
	 output logic [6:0] HEX4,
	 output logic [6:0] HEX5,
	 
	 // ===== NUEVAS SALIDAS VGA =====
 	 output logic vga_hsync,
 	 output logic vga_vsync,
	 output logic vga_clk,
	 output logic vga_blank_n,
	 output logic vga_sync_n,
 	 output logic [3:0] vga_r,
 	 output logic [3:0] vga_g,
 	 output logic [3:0] vga_b
);
    // Señales Internas
    logic clk_cpu;
    logic [31:0] pc, next_pc, inst, imm32, readData1, readData2, aluResult, memReadData, writeData;
	 logic [31:0] a0_val;
    logic [3:0]  alu_control;
    logic [1:0]  aluOp, jumpType;
    logic regWrite, aluSrc, memRead, memToReg, branch, memWrite, zero, jump, lt, ltu;
    logic        memUnsigned;
    logic [1:0]  memSize;
    logic [31:0] valor_a_mostrar;
    logic ebreak;
    logic [1023:0] reg_flat;
    logic ebreak_signal;
    logic [6:0] hex0_raw, hex1_raw, hex2_raw, hex3_raw, hex4_raw, hex5_raw;
    
    // Generador de pulso limpio para el boton
    assign clk_cpu = ~clk_button; // KEY0 es activo en bajo.
   
      
    // Logica de Selección de Visualización (Multiplexor de 3 vías)
    always_comb begin
        if (SW[2])
            valor_a_mostrar = inst;      // Muestra la instrucción (32 bits)
        else if (SW[1])
            valor_a_mostrar = a0_val;    // Muestra el registro a0 (x10)
        else
            valor_a_mostrar = pc;        // Muestra el PC
    end
    
    // Evaluador de Saltos Condicionales
    logic branch_cond, take_branch;
    always_comb begin
        if (branch) begin
            case (inst[14:12])
                3'b000: branch_cond = zero;  // beq
                3'b001: branch_cond = !zero; // bne
                3'b100: branch_cond = lt;    // blt
                3'b101: branch_cond = !lt;   // bge
                3'b110: branch_cond = ltu;   // bltu
                3'b111: branch_cond = !ltu;  // bgeu
                default: branch_cond = 1'b0;
            endcase
        end else begin
            branch_cond = 1'b0;
        end
    end
    
    assign take_branch = branch && branch_cond;
    
    // Cálculo del siguiente PC
    always_comb begin
        if (jump && jumpType == 2'b10) // JALR
            next_pc = (readData1 + imm32) & ~32'h1; // Pone el LSB en 0
        else if (jump || take_branch)  // JAL o Branch
            next_pc = pc + imm32;
        else                           // Normal
            next_pc = pc + 4;
    end
    
    PC pc_unit(.clk(clk_cpu), .reset(reset), .next_pc(next_pc), .pc(pc));

    // Memoria de Instrucciones
    logic [31:0] rom [0:127];
    initial begin
        $readmemh("programa.hex", rom); 
    end
    assign inst = rom[pc >> 2];

    // Instancias de Control y Datapath
    ControlUnit ctrl(
        .opcode(inst[6:0]), .branch(branch), .memRead(memRead), 
        .memToReg(memToReg), .memWrite(memWrite), .aluSrc(aluSrc), 
        .regWrite(regWrite), .jump(jump), .aluOp(aluOp), .jumpType(jumpType), .ebreak(ebreak)
    ); 

    ImmGen igen(.inst(inst), .imm32(imm32));
    
    RegisterFile regs(
        .regWrite(regWrite), .rs1(inst[19:15]), .rs2(inst[24:20]), 
        .rd(inst[11:7]), .writeData(writeData), .readData1(readData1), .readData2(readData2),.debug_a0(a0_val),
        .reg_file_flat(reg_flat)
    );

    ALUControl actrl(
        .aluOp(aluOp), .funct3(inst[14:12]), .funct7(inst[31:25]), .aluControl(alu_control)
    );
    
    ALU alu_u(
        .A(jumpType == 2'b01 || jumpType == 2'b10 ? pc : readData1), // Para JAL/JALR
        .B(aluSrc ? imm32 : readData2), 
        .aluControl(alu_control), .result(aluResult), 
        .zero(zero), .lt(lt), .ltu(ltu)
    );
    
    always_comb begin
        memSize = 2'b10;
        memUnsigned = 1'b0;

        if (inst[6:0] == 7'h03 || inst[6:0] == 7'h23) begin
            case (inst[14:12])
                3'b000: memSize = 2'b00; // LB/SB
                3'b001: memSize = 2'b01; // LH/SH
                3'b010: memSize = 2'b10; // LW/SW
                3'b100: begin
                    memSize = 2'b00;
                    memUnsigned = 1'b1; // LBU
                end
                3'b101: begin
                    memSize = 2'b01;
                    memUnsigned = 1'b1; // LHU
                end
                default: ;
            endcase
        end
    end
    
    DataMemory dmem(
        .we(memWrite), .isUnsigned(memUnsigned), .size(memSize),
        .address(aluResult), .writeData(readData2), .readData(memReadData)
    );
    
    // Multiplexor final de escritura a registro (incluye JAL/JALR y AUIPC)
    always_comb begin
        if (jump) 
            writeData = pc + 4; // Guarda direccion de retorno
        else if (inst[6:0] == 7'h17) 
            writeData = pc + imm32; // AUIPC
        else if (memToReg) 
            writeData = memReadData; // Loads
        else 
            writeData = aluResult; // Tipo R/I
    end

    // Salidas Físicas
    assign LEDR[9:0] = aluResult[9:0];
    assign ebreak_signal = ebreak;  // Señal de EBREAK para debugging
    decodificador_7seg dec0(.binario(valor_a_mostrar[3:0]), .segmentos(hex0_raw));
    decodificador_7seg dec1(.binario(valor_a_mostrar[7:4]), .segmentos(hex1_raw));
	decodificador_7seg dec2(.binario(valor_a_mostrar[11:8]),  .segmentos(hex2_raw));
    decodificador_7seg dec3(.binario(valor_a_mostrar[15:12]), .segmentos(hex3_raw));
    decodificador_7seg dec4(.binario(valor_a_mostrar[19:16]), .segmentos(hex4_raw));
    decodificador_7seg dec5(.binario(valor_a_mostrar[23:20]), .segmentos(hex5_raw));
  

    // ============================================================================
    // MONITOR VGA DE DEBUG CONECTADO AL CORE
    // ============================================================================
    vga_debug_monitor debug_vga (
        .clk50(CLOCK_50),
        .reset(reset),
        .pc(pc),
        .inst(inst),
        .reg_file_flat(reg_flat),
        .frame_pulse(),
        .line_pulse(),
        .pixel_clk(vga_clk),
        .blank_n(vga_blank_n),
        .sync_n(vga_sync_n),
        .hsync(vga_hsync),
        .vsync(vga_vsync),
        .red(vga_r),
        .green(vga_g),
        .blue(vga_b)
    );

endmodule
