# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Counter Test")

    # 1. Initialize clock (e.g., 10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # 2. Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0      # input_reg
    dut.uio_in.value = 0     # bit 0: load, bit 1: output_enable
    dut.rst_n.value = 0      # Active-low reset (asserted)

    dut._log.info("Testing Asynchronous Reset")
    await Timer(20, units="ns") # Small delay, not waiting for clock
    
    # Release reset
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Assert uio_in[1] (output_enable) to read the output
    dut.uio_in.value = 0b00000010
    await ClockCycles(dut.clk, 1)
    
    # The output should be 0 immediately after reset
    assert dut.uo_out.value == 0, f"Failed reset: uo_out is {dut.uo_out.value}"
    assert dut.uio_oe.value == 255, f"Failed enable: uio_oe is {dut.uio_oe.value}"

    dut._log.info("Testing Synchronous Load")
    dut.ui_in.value = 42            # Set input_reg to 42
    dut.uio_in.value = 0b00000011   # Assert load (bit 0) and output_enable (bit 1)
    
    await ClockCycles(dut.clk, 1)   # Wait one clock cycle
    
    assert dut.uo_out.value == 42, f"Failed load: expected 42, got {dut.uo_out.value}"

    dut._log.info("Testing Incrementation")
    dut.uio_in.value = 0b00000010   # De-assert load (bit 0), keep output_enable (bit 1)
    
    await ClockCycles(dut.clk, 5)   # Let it count for 5 cycles
    
    # 42 + 5 = 47
    assert dut.uo_out.value == 47, f"Failed counting: expected 47, got {dut.uo_out.value}"

    dut._log.info("Testing Tri-State Output Enable")
    dut.uio_in.value = 0b00000000   # De-assert output_enable (bit 1)
    
    await ClockCycles(dut.clk, 1)
    
    # uo_out should be forced to 0
    assert dut.uo_out.value == 0, f"Failed OE on uo_out: expected 0, got {dut.uo_out.value}"
    
    # uio_oe should be forced to 0 (high impedance on the pads)
    assert dut.uio_oe.value == 0, f"Failed OE on uio_oe: expected 0, got {dut.uio_oe.value}"
    
    # However, internally, it should still be counting! (47 + 1 = 48)
    dut.uio_in.value = 0b00000010   # Re-assert output_enable (bit 1)
    await ClockCycles(dut.clk, 1)
    
    # 48 + 1 (from re-assert cycle) = 49
    assert dut.uo_out.value == 49, f"Failed background counting: expected 49, got {dut.uo_out.value}"

    dut._log.info("Test passed successfully!")