import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Counter Test")

    # Start 10 MHz clock (100 ns period)
    clock = Clock(dut.clk, 100, unit="ns")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0      # ui_in[0]=load_input, ui_in[1]=output_enable
    dut.uio_in.value = 0     # input_reg data on uio_in
    dut.rst_n.value = 0      # Active-low reset asserted

    dut._log.info("Testing Asynchronous Reset")
    await Timer(50, unit="ns")
    
    # Assert output_enable to check reset output state
    dut.ui_in.value = 0b00000010  # output_enable = 1
    await Timer(1, unit="ns")
    assert dut.uio_oe.value == 255, f"uio_oe should be enabled, got {dut.uio_oe.value}"
    assert dut.uio_out.value == 0, f"Reset failed: uio_out is {dut.uio_out.value}"

    # Release reset
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Testing Synchronous Load")
    dut.uio_in.value = 42         # Target value on uio_in
    dut.ui_in.value = 0b00000001  # load_input = 1, output_enable = 0
    
    await ClockCycles(dut.clk, 1)
    await Timer(1, unit="ns")
    
    # During load, uio_oe MUST be 0 to prevent bus contention
    assert dut.uio_oe.value == 0, f"uio_oe must be 0 during load, got {dut.uio_oe.value}"

    dut._log.info("Testing Output Enable & Incrementation")
    dut.ui_in.value = 0b00000010  # load_input = 0, output_enable = 1
    await Timer(1, unit="ns")
    assert dut.uio_out.value == 42, f"Load value failed: expected 42, got {dut.uio_out.value}"

    await ClockCycles(dut.clk, 5) # 42 + 5 = 47
    await Timer(1, unit="ns")
    assert dut.uio_out.value == 47, f"Counting failed: expected 47, got {dut.uio_out.value}"

    dut._log.info("Testing Pad Driver High Impedance (uio_oe = 0)")
    dut.ui_in.value = 0b00000000  # output_enable = 0
    await Timer(1, unit="ns")
    
    # Check that pad drivers enter High Impedance (uio_oe = 0)
    assert dut.uio_oe.value == 0, f"OE disable failed: expected 0, got {dut.uio_oe.value}"

    dut._log.info("Testing Background Counting While Disabled")
    await ClockCycles(dut.clk, 2) # Count 2 cycles in background (47 + 2 = 49)
    
    dut.ui_in.value = 0b00000010  # Re-enable output
    await Timer(1, unit="ns")
    assert dut.uio_out.value == 49, f"Background count failed: expected 49, got {dut.uio_out.value}"

    dut._log.info("All tests passed!")