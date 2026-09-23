/*
 * Copyright (c) 2026 Aaron Snider
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_8bit_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Signals to match counter implementation
  wire [7:0] input_reg     = uio_in;
  wire       load_input    = ui_in[0];
  wire       output_enable = ui_in[1];

  // Internal counter register
  reg [7:0] count_8;

  // Enable loading through uio_in
  assign uio_oe  = (output_enable && !load_input) ? 8'b11111111 : 8'b00000000;

  // Reset, counting, and load logic
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      count_8 <= 8'b0;
    else if (load_input)
      count_8 <= input_reg;
    else
      count_8 <= count_8 + 1;
  end

  // Output logic
  assign uio_out = (output_enable) ? count_8 : 8'b0;

  // Unused 
  assign uo_out = 8'b0;
  wire _unused = &{ena, ui_in[7:2], 1'b0};

endmodule
