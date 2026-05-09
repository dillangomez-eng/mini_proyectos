module vga_debug_monitor(
    input  logic        clk50,
    input  logic        reset,
    input  logic [31:0] pc,
    input  logic [31:0] inst,
    input  logic [1023:0] reg_file_flat,
    output logic        frame_pulse,
    output logic        line_pulse,
    output logic        pixel_clk,
    output logic        blank_n,
    output logic        sync_n,
    output logic        hsync,
    output logic        vsync,
    output logic [3:0]  red,
    output logic [3:0]  green,
    output logic [3:0]  blue
);

    logic [31:0] reg_file [0:31];

    genvar g;
    generate
        for (g = 0; g < 32; g++) begin : unflatten
            assign reg_file[g] = reg_file_flat[g*32 +: 32];
        end
    endgenerate

    logic clk25;
    logic [9:0] h_count;
    logic [9:0] v_count;
    logic       visible;
    logic [6:0] col;
    logic [4:0] row;
    logic [2:0] font_col;
    logic [3:0] font_row;
    logic [7:0] char_code;
    logic [10:0] font_addr;
    logic [7:0] font_data;
    logic pixel_on;

    logic [7:0] font_rom [0:2047];

    function automatic logic [7:0] hex_to_ascii(input logic [3:0] nibble);
        if (nibble < 4'd10)
            hex_to_ascii = 8'd48 + nibble;
        else
            hex_to_ascii = 8'd55 + nibble;
    endfunction

    function automatic logic [3:0] nibble_at(
        input logic [31:0] value,
        input logic [2:0]  index
    );
        case (index)
            3'd0: nibble_at = value[31:28];
            3'd1: nibble_at = value[27:24];
            3'd2: nibble_at = value[23:20];
            3'd3: nibble_at = value[19:16];
            3'd4: nibble_at = value[15:12];
            3'd5: nibble_at = value[11:8];
            3'd6: nibble_at = value[7:4];
            default: nibble_at = value[3:0];
        endcase
    endfunction

    function automatic logic [7:0] reg_tens_ascii(input logic [4:0] value);
        if (value >= 5'd30)
            reg_tens_ascii = "3";
        else if (value >= 5'd20)
            reg_tens_ascii = "2";
        else if (value >= 5'd10)
            reg_tens_ascii = "1";
        else
            reg_tens_ascii = "0";
    endfunction

    function automatic logic [7:0] reg_ones_ascii(input logic [4:0] value);
        logic [4:0] ones;
        begin
            if (value >= 5'd30)
                ones = value - 5'd30;
            else if (value >= 5'd20)
                ones = value - 5'd20;
            else if (value >= 5'd10)
                ones = value - 5'd10;
            else
                ones = value;

            reg_ones_ascii = 8'd48 + ones;
        end
    endfunction

    always_ff @(posedge clk50 or posedge reset) begin
        if (reset)
            clk25 <= 1'b0;
        else
            clk25 <= ~clk25;
    end

    always_ff @(posedge clk25 or posedge reset) begin
        if (reset) begin
            h_count <= 10'd0;
            v_count <= 10'd0;
            frame_pulse <= 1'b0;
            line_pulse <= 1'b0;
        end else if (h_count == 10'd799) begin
            h_count <= 10'd0;
            line_pulse <= 1'b1;
            if (v_count == 10'd524)
                v_count <= 10'd0;
            else
                v_count <= v_count + 10'd1;
            frame_pulse <= (v_count == 10'd524);
        end else begin
            h_count <= h_count + 10'd1;
            frame_pulse <= 1'b0;
            line_pulse <= 1'b0;
        end
    end

    assign hsync   = ~((h_count >= 10'd656) && (h_count < 10'd752));
    assign vsync   = ~((v_count >= 10'd490) && (v_count < 10'd492));
    assign visible = (h_count < 10'd640) && (v_count < 10'd480);
    assign pixel_clk = clk25;
    assign blank_n   = visible;
    assign sync_n    = 1'b0;

    assign col      = h_count[9:3];
    assign row      = v_count[8:4];
    assign font_col = h_count[2:0];
    assign font_row = v_count[3:0];

    always_comb begin
        char_code = " ";

        case (row)
            // Fila 1: Título
            5'd1: begin
                case (col)
                    7'd2:  char_code = "D";
                    7'd3:  char_code = "E";
                    7'd4:  char_code = "B";
                    7'd5:  char_code = "U";
                    7'd6:  char_code = "G";
                    7'd8:  char_code = "V";
                    7'd9:  char_code = "G";
                    7'd10: char_code = "A";
                    default: char_code = " ";
                endcase
            end

            // Fila 3: PC e INST
            5'd3: begin
                case (col)
                    7'd2:  char_code = "P";
                    7'd3:  char_code = "C";
                    7'd5:  char_code = ":";
                    7'd7:  char_code = hex_to_ascii(nibble_at(pc, 3'd0));
                    7'd8:  char_code = hex_to_ascii(nibble_at(pc, 3'd1));
                    7'd9:  char_code = hex_to_ascii(nibble_at(pc, 3'd2));
                    7'd10: char_code = hex_to_ascii(nibble_at(pc, 3'd3));
                    7'd11: char_code = hex_to_ascii(nibble_at(pc, 3'd4));
                    7'd12: char_code = hex_to_ascii(nibble_at(pc, 3'd5));
                    7'd13: char_code = hex_to_ascii(nibble_at(pc, 3'd6));
                    7'd14: char_code = hex_to_ascii(nibble_at(pc, 3'd7));

                    7'd17: char_code = "I";
                    7'd18: char_code = "N";
                    7'd19: char_code = "S";
                    7'd20: char_code = "T";
                    7'd21: char_code = ":";
                    7'd23: char_code = hex_to_ascii(nibble_at(inst, 3'd0));
                    7'd24: char_code = hex_to_ascii(nibble_at(inst, 3'd1));
                    7'd25: char_code = hex_to_ascii(nibble_at(inst, 3'd2));
                    7'd26: char_code = hex_to_ascii(nibble_at(inst, 3'd3));
                    7'd27: char_code = hex_to_ascii(nibble_at(inst, 3'd4));
                    7'd28: char_code = hex_to_ascii(nibble_at(inst, 3'd5));
                    7'd29: char_code = hex_to_ascii(nibble_at(inst, 3'd6));
                    7'd30: char_code = hex_to_ascii(nibble_at(inst, 3'd7));
                    default: char_code = " ";
                endcase
            end

            // Filas 5..20: registros x0-x15 (columna izq) y x16-x31 (columna der)
            // row 5 → x0/x16, row 6 → x1/x17, ..., row 20 → x15/x31
            default: begin
                if (row >= 5'd5 && row <= 5'd20) begin
                    logic [4:0] ridx_l, ridx_r;  // índice registro izq y der
                    ridx_l = row - 5'd5;          // 0..15
                    ridx_r = ridx_l + 5'd16;      // 16..31

                    case (col)
                        // --- Columna izquierda: xNN : VVVVVVVV ---
                        7'd2:  char_code = "x";
                        7'd3:  char_code = reg_tens_ascii(ridx_l);
                        7'd4:  char_code = reg_ones_ascii(ridx_l);
                        7'd5:  char_code = ":";
                        7'd7:  char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd0));
                        7'd8:  char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd1));
                        7'd9:  char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd2));
                        7'd10: char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd3));
                        7'd11: char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd4));
                        7'd12: char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd5));
                        7'd13: char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd6));
                        7'd14: char_code = hex_to_ascii(nibble_at(reg_file[ridx_l], 3'd7));

                        // --- Columna derecha: xNN : VVVVVVVV ---
                        7'd17: char_code = "x";
                        7'd18: char_code = reg_tens_ascii(ridx_r);
                        7'd19: char_code = reg_ones_ascii(ridx_r);
                        7'd20: char_code = ":";
                        7'd22: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd0));
                        7'd23: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd1));
                        7'd24: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd2));
                        7'd25: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd3));
                        7'd26: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd4));
                        7'd27: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd5));
                        7'd28: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd6));
                        7'd29: char_code = hex_to_ascii(nibble_at(reg_file[ridx_r], 3'd7));

                        default: char_code = " ";
                    endcase
                end
            end
        endcase
    end

    initial begin
        $readmemh("font128.hex", font_rom);
    end

    assign font_addr = {char_code[6:0], font_row};
    assign font_data = font_rom[font_addr];
    assign pixel_on  = font_data[7 - font_col];

    always_comb begin
        if (visible && pixel_on) begin
            red   = 4'hF;
            green = 4'hF;
            blue  = 4'hF;
        end else if (visible) begin
            red   = 4'h0;
            green = 4'h2;
            blue  = 4'h6;
        end else begin
            red   = 4'h0;
            green = 4'h0;
            blue  = 4'h0;
        end
    end

endmodule
