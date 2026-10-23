# 🏋️ Gym Room Booking Occupancy

Find the highest number of bookings active at the same time. The function also
returns the start and end times of the first period when this maximum occurs.
It is written in pure Python and can be used in a larger application.

## 🚀 Quick start

Use Python 3.12 or later. Clone or download the repository, then import the
function from `occupancy.py`:

```python
from occupancy import max_occupancy

bookings = [(-2, 2), (0, 1), (5, 8), (6, 7)]
maximum, peak_start, peak_end = max_occupancy(bookings)

print(maximum, peak_start, peak_end)
# 2 0 1
```

The function returns three values:

```text
(maximum_occupancy, peak_start, peak_end)
```

`peak_start` and `peak_end` are the start and end times of the first period
with the maximum number of active bookings. For the example above, the result
is `(2, 0, 1)`: two bookings are active from time `0` up to (but not including)
time `1`.

No installation is needed to use the calculation. To run the tests, install
`pytest`:

```shell
python -m pip install pytest
```

## 🧪 Tests

Run the complete test suite from the repository root:

```shell
python -m pytest -q
```
