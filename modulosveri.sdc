# Synopsys Design Constraints File for modulosveri RISC-V Core
# Generated for Quartus II/Quartus Prime

# Define the main clock constraint
# 50 MHz clock (20 ns period)
create_clock -name CLOCK_50 -period 20.000 -waveform { 0.000 10.000 } [get_ports CLOCK_50]

# Generated VGA pixel clock (25 MHz)
create_generated_clock -name VGA_CLK25 -source [get_ports CLOCK_50] -divide_by 2 [get_ports vga_clk]

# Define asynchronous reset and button (no timing constraints needed)
set_false_path -from [get_ports reset]
set_false_path -from [get_ports clk_button]

# Set input/output delay constraints for data paths
set_input_delay -clock CLOCK_50 -max 5.0 [get_ports "SW*"]
set_input_delay -clock CLOCK_50 -min 0.0 [get_ports "SW*"]
set_output_delay -clock CLOCK_50 -max 5.0 [get_ports "LEDR*"]
set_output_delay -clock CLOCK_50 -max 5.0 [get_ports "HEX*"]
set_output_delay -clock CLOCK_50 -min 0.0 [get_ports "LEDR*"]
set_output_delay -clock CLOCK_50 -min 0.0 [get_ports "HEX*"]

