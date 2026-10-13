# Maximum Occupancy: Algorithm and Design Analysis

## Scope and contract

`max_occupancy` is a pure Python function that accepts a list of booking tuples
`(start, end)` and returns
`(maximum_occupancy, peak_start, peak_end)`. A booking represents the
half-open interval `[start, end)`: it is active at its start and inactive at
its end.

For valid non-empty input, the function returns the global maximum occupancy
and the bounds of the first chronological continuous period at that maximum.
For an empty list, it returns `(0, None, None)`. Invalid bookings reject the
whole call with `InvalidBookingError`, a `ValueError` subclass.

The calculation uses only the Python standard library. It does not perform
input/output, access external services or storage, or enforce business rules
about allowed clock ranges. In particular, there is no command-line or JSON
interface.

## Algorithm

The implementation validates every booking before building events. Each valid
booking contributes a start event and an end event. The events are sorted by
timestamp, with starts ordered before ends at the same timestamp.

The sweep visits events in chronological order and processes every event at a
timestamp before measuring occupancy for the interval until the next distinct
timestamp. This grouped measurement is important: the interval
`[timestamp, next_timestamp)` has positive duration, and transient intermediate
counts at a shared timestamp must not be mistaken for occupancy over an
interval.

For each measured interval:

1. If occupancy is greater than the maximum seen so far, record this interval
   as the first interval at the new global maximum.
2. If occupancy equals the maximum and the interval starts exactly where the
   recorded peak ends, extend that peak.
3. Otherwise, keep the existing peak. In particular, an equal maximum reached
   later after a gap does not replace the first peak.

Events at the final timestamp have no following interval to measure. The sweep
therefore does not treat that endpoint as a positive-duration interval.

## Complexity

Let `n` be the number of bookings.

- Validation inspects each booking and takes `O(n)` time.
- Event construction creates `2n` entries and takes `O(n)` time and space.
- Sorting `2n` events takes `O(n log n)` time.
- The sweep processes each event once and takes `O(n)` time.

The total time complexity is **`O(n log n)`**. The event list uses **`O(n)`**
auxiliary space; the sweep's counters and peak bounds use `O(1)` additional
space. The input list and its booking tuples are not modified. For an empty
list, the function returns immediately in `O(1)` time and space.

The specification sets no maximum booking count or target latency. The
complexity describes how work scales; it does not imply a numeric performance
threshold.

## Design decisions

| Decision | Reason |
|---|---|
| Use a sorted event sweep with two events per booking. | It calculates concurrency without comparing every booking pair, giving `O(n log n)` time instead of a quadratic pairwise approach. |
| Interpret bookings as `[start, end)`. | This includes the start and excludes the end, as required by the contract. |
| Sort starts before ends at equal timestamps and measure only after the whole timestamp group. | This gives deterministic event ordering without counting a zero-duration transient state as an overlap. |
| Retain events for every input entry, including duplicates. | Each duplicate booking is an independent reservation and must contribute independently. |
| Validate the complete list before constructing events or calculating a result. | An invalid booking must reject the entire call rather than yield a partial result. |
| Explicitly reject booleans as well as non-integer times. | In Python, `bool` is a subclass of `int`, but boolean booking times are invalid under the contract. |
| Accept negative integer times when `start < end`. | Time-range business policies are outside this calculation's scope. |
| Preserve the first maximum period. | A later separated interval at the same maximum does not replace the first chronological one; a contiguous interval extends it. |
| Keep the function pure and standard-library-only. | The calculation remains deterministic and independently testable, without external I/O or runtime dependencies. |

## Boundary cases

| Case | Expected behavior |
|---|---|
| Empty booking list | Return `(0, None, None)` without raising an error. |
| One valid booking `(start, end)` | Return `(1, start, end)`. |
| Partially overlapping bookings | Count every active booking on each positive-duration interval and report the largest count. |
| Consecutive bookings where one ends as another starts | Do not count them as overlapping at the shared instant. |
| Several starts or ends at one timestamp | Process the complete timestamp group before measuring occupancy to the next distinct timestamp. |
| A maximum sustained across booking-change timestamps | Extend the peak bounds across adjacent intervals that remain at the global maximum. |
| Several separated periods with the same maximum | Return the earliest period and leave later equal periods unselected. |
| Start equal to or greater than end | Reject the booking; a booking must have `start < end`. |
| A booking with missing or extra time values | Reject the booking because it must contain exactly a start and an end. |
| Non-integer time | Reject the entire input with an explicit validation error. |
| Boolean time | Reject the entire input, even though `bool` is an integer subtype in Python. |
| Invalid booking among valid bookings | Raise an error identifying the invalid booking and reason; do not return a partial result. |
| Valid booking with negative times | Accept it when both times are integers and `start < end`. |
| Duplicate bookings | Count every entry independently; do not merge or discard duplicates. |

The validation error message follows
`Invalid booking at index {index} ({booking!r}): {reason}`. The index is
zero-based, and the reason identifies the failed rule.

## Compatibility characterization
The following existing and added tests record the behavior to preserve before
the optimization work:

| Behavior | Reference tests |
|---|---|
| Empty input returns `(0, None, None)`. | `test_empty_bookings_return_zero_occupancy_without_peak_bounds` |
| Booking shape, time types, booleans, and `start < end` are validated with the exact error class and message. | `test_booking_without_start_and_end_times_raises_identifying_error`, `test_booking_with_non_integer_or_boolean_time_raises_identifying_error`, `test_booking_with_invalid_order_raises_identifying_error` |
| The first invalid booking in input order wins; within a booking, `start` is checked before `end`. | `test_first_invalid_booking_in_input_order_is_reported`, `test_validation_checks_start_before_end_when_both_are_invalid` |
| Invalid input rejects the whole call, including when valid bookings precede the invalid one. | `test_mixed_valid_and_invalid_bookings_reject_the_entire_input` |
| Negative integer times and duplicate bookings remain valid and count independently. | `test_valid_booking_with_negative_times_passes_validation`, `test_identical_bookings_each_contribute_to_occupancy` |
| Shared endpoints follow half-open interval semantics; same-instant events are grouped and starts sort before ends. | `test_consecutive_bookings_do_not_overlap_at_shared_instant`, `test_all_events_at_shared_instant_are_applied_before_measuring`, `test_sorted_events_place_starts_before_ends_at_shared_instant` |
| A continuous maximum extends across changes, while separated equal maxima return the first period. | `test_maximum_period_extends_across_change_instants`, `test_first_of_separated_equal_maximum_periods_is_returned` |
| Repeated calls are deterministic and the input bookings and entries are not modified. | `test_repeated_calls_with_the_same_bookings_return_the_same_result`, `test_calculation_does_not_modify_bookings_or_their_entries` |

## Functional requirement coverage

| Requirement | Design and behavior |
|---|---|
| RF-1 — Calculate maximum occupancy | The sweep counts active bookings on each interval between distinct event timestamps and retains the largest count. |
| RF-2 — Apply interval semantics | Bookings use `[start, end)`; occupancy is measured after the complete timestamp group, so an ending booking is not active at its end. |
| RF-3 — Report the first maximum period | Record a new higher maximum, extend it across contiguous intervals at that maximum, and retain it over later separated ties. |
| RF-4 — Resolve empty lists | Return `(0, None, None)` for an empty list. |
| RF-5 — Reject invalid inputs | Reject malformed bookings, invalid time values, and `start >= end`; validation precedes calculation and errors identify the offending booking and reason. |
| RF-6 — Define same-instant event ordering | Sort start events before end events at equal timestamps and evaluate only after all events at that timestamp are processed. |
| RF-7 — Define duplicate handling | Keep separate start and end events for each input entry, including identical bookings. |
| RF-8 — Define valid integer semantics | Accept integer times, reject non-integers, and explicitly reject booleans. |
| RF-9 — Define negative instants | Accept negative integer times when the booking otherwise satisfies `start < end`; range restrictions belong to callers. |
