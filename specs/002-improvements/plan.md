# Implementation Plan: Occupancy Calculation Improvements

## 1. Scope and governing requirements

This plan translates the active improvement specification into an implementation
outline. The change is limited to validating bookings while creating their
events in one input traversal and representing event labels as integers. All
existing observable behavior remains in scope for preservation: the result
contract, validation behavior, error details, tie-breaking, interval semantics,
determinism, and input immutability. (RF-1–RF-3)

The calculation remains a pure function using only the Python standard library.
No external interfaces, I/O, storage, or new runtime dependencies are part of
the work. The algorithm must retain `O(n log n)` time and `O(n)` space. No
numeric latency, memory, or input-size target, nor a benchmark requirement, is
introduced. (Constitution; non-functional requirements)

The project constitution requires tests to pass at the end of the task and
requires detailed English documentation of complexity, decisions, and boundary
cases in `README.md` and `ANALYSIS.md`. These documentation requirements remain
applicable without expanding the calculation's functional scope.

## 2. Existing project structure and proposed changes

### Existing

The inspected repository contains:

- `docs/constitution.md` — project constraints.
- `specs/001-occupancy-mvp/spec.md` and `specs/001-occupancy-mvp/plan.md` — the
  existing calculation contract and its implementation plan.
- `specs/002-improvements/spec.md` — the active requirements for this change.
- `occupancy.py` — the public calculation, validation, event construction, and
  occupancy sweep.
- `tests/test_occupancy.py` — calculation, validation, and event-order tests.
- `README.md` — a short project description.

The current calculation validates bookings in one traversal and then calls a
separate event-building operation that traverses the bookings again. Event
labels are currently text values. Tests directly check the sorted event
representation, so those expectations must change together with the internal
representation. There is no `ANALYSIS.md` in the inspected repository.

### Proposed changes

| Path | Status | Responsibility and requirement coverage |
|---|---|---|
| `occupancy.py` | Update | Combine per-booking validation and event extraction into one traversal; represent start/end labels with integers; retain sorting semantics, occupancy calculation, public behavior, and purity. (RF-1–RF-3) |
| `tests/test_occupancy.py` | Update | Preserve regression coverage and update event representation assertions; verify validation order, same-instant ordering, results, errors, determinism, and input immutability. (RF-1–RF-3) |
| `README.md` | Update | Document the existing public behavior and the improvement at a user-facing level in English, without introducing new interfaces or numeric performance guarantees. (Constitution; RF-1–RF-3) |
| `ANALYSIS.md` | Create | Explain the one-pass validation/event extraction, integer event labels, complexity, decisions, and relevant boundary cases in English. (Constitution; RF-1–RF-3) |

No new runtime package, command-line interface, service, persistence layer, or
external input adapter is proposed.

## 3. Preserved input and output behavior

Keep the existing public function signature and return shape unchanged. Empty
input continues to return `(0, None, None)`. Valid non-empty input continues to
return the maximum occupancy and the first continuous period in which that
maximum is reached. The calculation continues to interpret bookings as
semi-open intervals `[start, end)`. (RF-3; existing public contract)

Preserve the currently supported booking rules: exactly two integer booking
times, with booleans rejected and `start < end`; valid negative times remain
accepted. Duplicates remain independent entries. The function must not mutate
the booking list or its entries, and repeated calls with the same input must
remain deterministic. (RF-3)

Invalid input continues to reject the whole call. Preserve the existing
first-invalid-booking behavior in input order, zero-based index, error class,
and message format and reason text. No partial result may be returned. The
single traversal must not change which invalid booking is reported. (RF-1,
RF-3; existing validation behavior)

## 4. Change outline

1. Review the current validation and event-construction flow and identify where
   each booking can be validated and its start and end events extracted during
   the same visit. Do not introduce a second validation traversal. (RF-1)
2. Build the complete event collection during that traversal. If validation
   fails, raise the existing error for the first invalid booking; do not run
   the occupancy calculation or return a partial result. (RF-1, RF-3)
3. Replace textual start/end labels in the event representation with integer
   labels. Keep event meaning internal and ensure sorting still places starts
   before ends at equal timestamps without relying on an accidental numeric
   ordering that could reverse the required precedence. (RF-2)
4. Keep the existing timestamp grouping and occupancy sweep semantics. Measure
   occupancy after all events at a timestamp have been applied, preserving
   `[start, end)` behavior and first-peak selection. (RF-2, RF-3)
5. Update focused regression tests and documentation, then run the complete
   project test suite as the completion gate. (Constitution; completion
   criteria)

The event-label integer values are deliberately left to implementation. No
public return value or error message may expose those internal values. (RF-2)

## 5. Technical decisions and constraints

| Decision | Rationale | Alternative not selected | Coverage |
|---|---|---|---|
| Validate each booking while extracting its two events during the same input traversal. | Removes the separate validation pass while preserving whole-input rejection and first-invalid selection. | Validate the full input, then traverse it again to build events. | RF-1 |
| Use integer values for event labels. | Avoids storing textual labels and satisfies the specified event representation. | Retain text labels or expose event labels through the public result. | RF-2 |
| Preserve start-before-end precedence at equal timestamps explicitly. | The required interval semantics are independent of whichever integer values represent the event labels. | Rely on an unspecified or incidental label ordering. | RF-2, RF-3 |
| Keep timestamp-grouped occupancy evaluation and existing peak selection. | Preserves semi-open intervals, continuous peak periods, and the first-period tie-break. | Measure transient occupancy between events at the same timestamp or alter peak selection. | RF-3 |
| Preserve existing validation errors and input behavior. | The improvement specification requires compatibility and the current project behavior defines concrete error details. | Change error type, message, invalid-booking precedence, accepted values, or input mutation behavior. | RF-1, RF-3 |
| Keep the standard-library-only pure calculation and avoid numeric performance targets. | Follows the constitution and the explicit scope of the active specification. | Add runtime dependencies, I/O, interfaces, or unapproved performance thresholds. | Constitution; non-functional requirements |

For `n` bookings, the change must keep event creation and validation at `O(n)`,
event sorting at `O(n log n)`, and the occupancy sweep at `O(n)`. The event
collection remains `O(n)` auxiliary space. The plan does not promise a measured
latency or memory reduction by a fixed amount. (Non-functional requirements)

## 6. Test strategy

Tests call the public function directly for behavior and use focused internal
event checks only where needed to verify the integer labels and deterministic
ordering. No tests require I/O, external services, storage, or CLI behavior.
Keep the algorithm standard-library-only and use the project's existing test
setup. (Constitution; RF-1–RF-3)

Planned verification:

| Test case | Expected verification | Coverage |
|---|---|---|
| Empty input | Returns `(0, None, None)`. | RF-1 |
| Valid single and overlapping bookings | Existing maximum and peak-period results remain unchanged. | RF-3 |
| Consecutive bookings with a shared endpoint | They are not counted as overlapping at that instant. | RF-2, RF-3 |
| Multiple starts and ends at one timestamp | All events are grouped and the established start-before-end precedence is retained. | RF-2, RF-3 |
| Equal maximum sustained across event timestamps | The returned peak remains one continuous period. | RF-3 |
| Separated periods with the same global maximum | The first chronological period remains selected. | RF-3 |
| Duplicate bookings | Each duplicate contributes independently. | RF-3 |
| Valid negative booking times | They remain accepted. | RF-3 |
| Malformed, non-integer, boolean, equal-bound, or reversed booking | The existing exception class and exact identifying message remain unchanged. | RF-1, RF-3 |
| Multiple invalid bookings | The earliest invalid entry in input order is reported. | RF-1, RF-3 |
| Valid entries preceding an invalid entry | The entire call fails without a partial result. | RF-1 |
| Event representation | Event labels are integers; start events still precede end events at equal timestamps. | RF-2 |
| Repeated calls and retained input | Results remain deterministic and the input remains unchanged. | RF-3 |
| Traversal structure | Review/test evidence confirms validation and event extraction share one input traversal, with no later pass to validate processed bookings. | RF-1 |

No benchmark threshold or maximum-size performance test is required because
none is defined by the specification. The full test suite must pass before the
change is complete. (Constitution; non-functional requirements)

## 7. Functional-requirement coverage matrix

| Requirement | Plan sections / decisions | Planned verification |
|---|---|---|
| RF-1 — Validate and obtain events in one traversal | Sections 2, 4, and 5: combine validation with event extraction and preserve whole-input rejection. | Mixed valid/invalid inputs; earliest invalid entry; structural confirmation of one traversal. |
| RF-2 — Use integer event labels | Sections 2, 4, and 5: integer labels with explicit same-timestamp precedence. | Integer-label assertions and start-before-end ordering at shared timestamps. |
| RF-3 — Preserve current functional contract | Sections 3–6: maintain result, intervals, validation, duplicate handling, determinism, and input immutability. | Existing behavior regression cases, errors, boundary cases, and full test suite. |
