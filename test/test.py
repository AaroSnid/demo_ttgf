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
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0      # Reset asserted (active-low)

    dut._log.info("Testing Asynchronous Reset")
    await Timer(50, unit="ns")
    assert dut.uo_out.value == 0, f"Reset failed: uo_out is {dut.uo_out.value}"

    # Release reset
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Testing Synchronous Load")
    dut.ui_in.value = 42
    dut.uio_in.value = 0b00000011  # load_input = 1, output_enable = 1
    
    await ClockCycles(dut.clk, 1)
    await Timer(1, unit="ns")  # Gate-level propagation delay
    
    assert dut.uo_out.value == 42, f"Load failed: expected 42, got {dut.uo_out.value}"

    dut._log.info("Testing Incrementation")
    dut.uio_in.value = 0b00000010  # load_input = 0, output_enable = 1
    
    await ClockCycles(dut.clk, 5)  # 42 + 5 = 47
    await Timer(1, unit="ns")
    
    assert dut.uo_out.value == 47, f"Counting failed: expected 47, got {dut.uo_out.value}"

    dut._log.info("Testing Output Enable (Disable Output)")
    dut.uio_in.value = 0b00000000  # output_enable = 0
    await Timer(1, unit="ns")
    
    assert dut.uo_out.value == 0, f"OE disable failed: expected 0, got {dut.uo_out.value}"

    dut._log.info("Testing Continued Counting While Disabled")
    await ClockCycles(dut.clk, 2)  # Count 2 cycles in background (47 + 2 = 49)
    
    dut.uio_in.value = 0b00000010  # Re-enable output
    await Timer(1, unit="ns")
    
    assert dut.uo_out.value == 49, f"Background count failed: expected 49, got {dut.uo_out.value}"

    dut._log.info("All tests passed!")