## How it works

An 8-bit synchronous counter that increments on every rising edge of `clk`. It has two override signals:

- `rst_n` (asynchronous, active-low): as soon as this goes low, `count_out` is forced to `0x00`, independent of the clock.
- `load` (synchronous, active-high): if high at a rising clock edge (and `rst_n` is high), the counter loads `data_in` instead of incrementing.

Priority order: async reset > synchronous load > increment. The count wraps from `0xFF` to `0x00`.

## How to test

1. Pulse `rst_n` low and confirm `count_out` goes to `0x00`.
2. Release reset, clock the counter, and confirm it increments by 1 each rising edge.
3. Set `data_in` to a test value, assert `load` for one cycle, and confirm `count_out` picks it up on the next edge.
4. Let the counter reach `0xFF` and confirm it wraps to `0x00` on the following edge.
5. Assert `rst_n` low between clock edges and confirm `count_out` clears immediately, without waiting for a clock edge.

## External hardware

None.
