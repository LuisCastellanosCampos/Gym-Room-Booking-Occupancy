# Room Booking Occupancy

Find out how many bookings overlap at most, and when the first busiest
stretch happens.

## Requirements

- Python 3.12 or later.
- The calculation uses only the Python standard library.
- `pytest` is required only to run the test suite.

## Installation

Clone or download this repository and run the following commands from its root.
No package installation is needed to use the calculation. To install the test
dependency, run:

```shell
python -m pip install pytest
```

## Usage

Import `max_occupancy` from `occupancy.py` and pass a list of `(start, end)`
integer tuples:

```python
from occupancy import max_occupancy

bookings = [(-2, 2), (0, 1), (5, 8), (6, 7)]
result = max_occupancy(bookings)
print(result)  # (2, 0, 1)
```

The returned tuple is
`(maximum_occupancy, peak_start, peak_end)`. For an empty list the result is
`(0, None, None)`. The calculation is a Python API; the project does not provide
a command-line interface.

Each booking uses the half-open interval `[start, end)`: its start is included
and its end is excluded. The reported peak is the first chronological
continuous period at the global maximum; adjacent intervals at that maximum
are reported as one period.

Every booking must contain exactly two integer times with `start < end`.
Boolean and other non-integer times are invalid; valid negative times are
accepted. Duplicate bookings count independently. If any booking is invalid,
the complete call raises `InvalidBookingError`, a `ValueError` subclass, with
the zero-based booking index, its value, and the reason. The input list is not
modified.

## Tests

Run the complete test suite from the repository root:

```shell
python -m pytest -q
```

## Video

Video link: [Add video link here](#)
