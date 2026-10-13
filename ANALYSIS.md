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

For empty input, `max_occupancy` returns `(0, None, None)` immediately. For
non-empty input, `_build_sorted_events` visits the booking list once. During
that visit it checks the booking shape, validates `start` and then `end`, checks
`start < end`, and appends the two events. An invalid booking raises immediately
with its input index and existing reason text. Events accumulated for earlier
bookings are local to the failing call: sorting and the occupancy sweep do not
run, and no partial result is returned.

Each event is a `(timestamp, integer_label)` tuple. `_START_EVENT` is `1` and
`_END_EVENT` is `0`. Sorting uses `(timestamp, event_label != _START_EVENT)`;
the second key explicitly puts starts first, even though the end label is the
smaller integer. The sweep recognizes event meaning using the same start label.
Neither label is exposed by `max_occupancy`.

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

Let `n` be the number of bookings and `m = 2n` the number of events.

- The single validation-and-extraction pass takes `O(n)` time and creates `m`
   events in `O(n)` space.
- Sorting `m` events takes `O(m log m) = O(n log n)` time.
- The occupancy sweep processes each event once in `O(m) = O(n)` time.

Therefore, total time is **`O(n log n)`** and auxiliary space is **`O(n)`**.
The event list and Python's temporary sorting keys/workspace are linear in the
number of events; sweep counters and peak bounds use `O(1)` additional space.
The input list and its booking tuples are not modified. Empty input takes
`O(1)` time and space.

This analysis counts bookings and treats integer comparisons as constant-time,
as is customary for fixed-width values. Python integers are arbitrary precision:
if timestamps have `b` bits, comparing them can also depend on `b`. For such
inputs, the `O(n log n)` bound describes the number of comparisons, not their
bit-level cost.

The specification sets no maximum booking count or target latency. The
complexity describes how work scales; it does not imply a numeric performance
threshold.

## Design decisions

| Decision | Reason |
|---|---|
| Use a sorted event sweep with two events per booking. | It calculates concurrency without comparing every booking pair, giving `O(n log n)` time instead of a quadratic pairwise approach. |
| Validate and extract events in one input pass. | It removes the old separate validation traversal; validation order remains input order. |
| Use integer event labels, with start `1` and end `0`. | Labels are internal and their values are not specified. Reversing their numeric order makes it important that precedence is encoded explicitly, rather than inferred from integer comparison. |
| Sort starts before ends and measure only after a whole timestamp group. | Bookings are half-open `[start, end)`. Intermediate counts at the same instant do not describe a positive-duration interval. |
| Retain events for every input entry, including duplicates. | Each duplicate booking is an independent reservation and must contribute independently. |
| Raise on the first invalid booking and do not return accumulated events. | This preserves the zero-based first-error rule and whole-call rejection without exposing a partial result. |
| Reject booleans explicitly. | In Python, `bool` is a subclass of `int`, but boolean booking times are invalid under the contract. Other `int` instances are accepted by `isinstance`. |
| Accept negative integer times when `start < end`. | Time-range business policies are outside this calculation's scope. |
| Preserve the first maximum period and extend it across adjacent intervals. | This follows the established tie-break and reports a continuous peak rather than separate fragments. |
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

## Adverse and surprising cases

The meaningful cost and behavior risks are concentrated in input size, event
ordering, and caller assumptions:

| Situation | Effect or possible surprise | Coverage |
|---|---|---|
| A very large booking list | The sort is the dominant CPU cost. The implementation stores two event tuples per booking, plus linear temporary sorting data, so memory pressure may arrive before the asymptotic bound becomes a practical guarantee. | The one-pass test verifies traversal count, not scale or memory. No benchmark or maximum input size is specified. |
| Timestamps in an order that does not form long sorted runs | Sorting can approach its `O(n log n)` comparison bound. Already ordered runs may be cheaper due to Python's adaptive sort, but callers should not rely on that. | Correctness and determinism are tested; adversarial performance is not. |
| Extremely large integer timestamps | The number of comparisons still follows the event-sort bound, but each comparison can cost more as integer bit length grows. | Negative and ordinary-sized integers are covered; huge-integer performance is not. |
| An invalid booking late in a large input | Earlier valid bookings have already been validated and have events accumulated before the error is raised. That local work and memory are spent, but no sort, sweep, or partial result occurs. | Mixed valid/invalid positions and first-error selection are tested; failure-path resource use is not benchmarked. |
| Many identical bookings or many events at one timestamp | Duplicates intentionally increase occupancy independently. The sweep processes every event in the timestamp group before measuring the next interval; transient counts within the group are not reported. | Duplicate, coincident-event, and shared-endpoint behavior is covered by `test_identical_bookings_each_contribute_to_occupancy`, `test_all_events_at_shared_instant_are_applied_before_measuring`, and `test_sorted_events_place_starts_before_ends_at_shared_instant`. |
| A caller expects closed intervals, duplicate removal, or the latest tied peak | Results may appear surprising: shared endpoints are not overlap duration, duplicates count, and the first separated period at the maximum wins. | Half-open endpoints, duplicates, continuous peaks, and separated ties have regression tests. |
| A booking value is not a sequence, such as `None` | The public annotation is `list[tuple[int, int]]`; for values outside that shape, `len(booking)` may raise a native `TypeError` rather than `InvalidBookingError`. | Short and long tuple shapes are tested; non-sequence booking objects are not. Callers should honor the annotated input shape. |

These cases matter more than a long list of synthetic boundaries: the large
input cases stress the event collection and sort, while the same-timestamp,
duplicate, and separated-peak cases are the places where plausible alternate
interpretations would change the answer.

## Decisions where the specification leaves room

- The event labels use `1` for start and `0` for end. The specification
   requires integers but chooses no values. The sort key explicitly prioritizes
   the start label, so a different numeric assignment would not change
   precedence.
- A continuous maximum is one period even when booking events divide it into
   adjacent sub-intervals. If the same maximum recurs after a gap, the earliest
   period remains the result. This is retained from the existing behavior.
- Negative integers are valid and no clock range, timezone, or normalization is
   inferred. Such policy belongs to the caller.
- Booleans are rejected despite `bool` being an `int` subclass; `start` is
   checked before `end`, and shape is checked before either endpoint. This keeps
   error selection deterministic when more than one field is invalid.
- An invalid booking aborts immediately. No partial result is useful under the
   all-or-nothing contract, and no error is deferred to a later booking.
- No benchmark threshold, maximum booking count, runtime dependency, or CLI is
   introduced because none is part of the active specification.

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

## Verification coverage

| Requirement | Behavior preserved | Reference tests |
|---|---|---|
| RF-1 — Validate and extract events in one traversal | One iteration over the booking list; invalid input raises without a public partial result; empty input retains its result. | `test_each_booking_is_validated_during_single_event_extraction_pass`, `test_mixed_valid_and_invalid_bookings_reject_the_entire_input`, `test_empty_bookings_return_zero_occupancy_without_peak_bounds` |
| RF-2 — Use integer event labels | Internal labels are integers; starts precede ends at equal timestamps even though the end label is numerically smaller; labels do not appear in the public result. | `test_sorted_events_keep_coincident_starts_and_ends`, `test_sorted_events_place_starts_before_ends_at_shared_instant`, `test_all_events_at_shared_instant_are_applied_before_measuring` |
| RF-3 — Preserve the functional contract | Exact results and errors, half-open endpoints, duplicate and negative-time handling, first/continuous peak selection, determinism, and input immutability. | The tests in the compatibility characterization table above, including the validation-order, peak-period, duplicate, negative-time, repeat-call, and immutability tests. |

The suite does not test memory ceilings, benchmark adversarial sorts, huge
integer performance, or booking objects outside the annotated tuple shape.
Those gaps are deliberate: the specification defines no numeric performance
target and the public API is typed for `list[tuple[int, int]]`. The non-sequence
case is called out separately because its native exception differs from the
custom validation error.

## AI tools used

GitHub Copilot in VS Code was the only AI tool used. It helped inspect the
active specification, plan, constitution, implementation, and tests; compare
the documented behavior with the code; and draft and revise this analysis.
No other AI assistants or generative services were used. The test suite was
run locally with `python -m pytest -q`; pytest is a test tool, not an AI tool.
