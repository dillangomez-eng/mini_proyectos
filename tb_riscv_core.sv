`timescale 1ns / 1ps

module tb_riscv_core;

    // Señales del DUT (Device Under Test)
    logic CLOCK_50;
    logic clk_button;
    logic reset;
    logic [1:0] SW;
    logic [9:0] LEDR;
    logic [6:0] HEX0, HEX1, HEX2, HEX3, HEX4, HEX5;
    logic vga_hsync, vga_vsync, vga_clk, vga_blank_n, vga_sync_n;
    logic [3:0] vga_r, vga_g, vga_b;

    // Instancia del módulo RISCV_Core
    RISCV_Core dut (
        .CLOCK_50(CLOCK_50),
        .clk_button(clk_button),
        .reset(reset),
        .SW(SW),
        .LEDR(LEDR),
        .HEX0(HEX0),
        .HEX1(HEX1),
        .HEX2(HEX2),
        .HEX3(HEX3),
        .HEX4(HEX4),
        .HEX5(HEX5),
        .vga_hsync(vga_hsync),
        .vga_vsync(vga_vsync),
        .vga_clk(vga_clk),
        .vga_blank_n(vga_blank_n),
        .vga_sync_n(vga_sync_n),
        .vga_r(vga_r),
        .vga_g(vga_g),
        .vga_b(vga_b)
    );

    // Generador de clock
    initial begin
        CLOCK_50 = 0;
        forever #10 CLOCK_50 = ~CLOCK_50; // 50MHz clock
    end

    // Simulación
    initial begin
        // Inicialización
        reset = 1;
        clk_button = 0;
        SW = 2'b00; // Mostrar PC inicialmente

        // Reset
        #100 reset = 0;

        // Ejecutar el programa paso a paso
        // El clk_button es manual, así que togglearlo para avanzar
        repeat (100) begin // Ejecutar 100 ciclos o hasta que termine
            #20 clk_button = 1;
            #20 clk_button = 0;

            // Mostrar el valor de a0 en cada paso
            $display("PC: %h, Inst: %h, a0: %h", dut.pc, dut.inst, dut.a0_val);

            // Si llega a ebreak o fin, detener
            if (dut.ebreak || dut.pc >= 32'h00000100) begin
                $display("Programa terminado. a0 final: %h", dut.a0_val);
                $finish;
            end
        end

        $finish;
    end

endmodule