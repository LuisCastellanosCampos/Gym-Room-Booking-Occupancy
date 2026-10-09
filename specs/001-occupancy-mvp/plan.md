# Implementation Plan: Maximum Concurrent Occupancy

## 1. Scope and governing requirements

This plan translates the active specification into an implementation outline
without changing its behavior or adding interfaces. The implementation is a
pure Python calculation for valid room-booking intervals. It does not receive
bookings from external systems, perform I/O, or apply business rules about
permitted clock ranges.

The governing constraints are Python 3.12 or later, the Python standard library
for the algorithm, a pure and independently testable core, and English
technical documentation. The algorithm will have no network, database,
storage, or user-interface dependencies. (RF-1–RF-9)

The specification defines no maximum booking count or target latency; document
the asymptotic cost and assess efficiency qualitatively rather than introducing
a numeric performance requirement. (RF-1, RF-3; non-functional requirements)

## 2. Existing project structure and proposed modules

### Existing

The inspected repository currently contains:

- `docs/constitution.md` — project constraints.
- `specs/001-occupancy-mvp/spec.md` — active requirements.
- `README.md` — a short project description.
- `AGENTS.md` — local development instructions.
- `skills/spec-generator/` — specification-authoring guidance.

There is currently no Python source module, test suite, `ANALYSIS.md`, or
packaging/build configuration in the repository. In particular, there is no
existing `occupancy` module or executable entry point in the code to verify.
`AGENTS.md` mentions `python -m occupancy`, but the referenced module is absent;
this plan does not treat that instruction as an existing, verified interface
and does not propose implementing a CLI. The calculation remains the sole
product behavior in scope. (RF-1–RF-9; out of scope)

### Proposed implementation structure

| Path | Status | Responsibility and requirement coverage |
|---|---|---|
| `occupancy.py` | Create | Define the public `max_occupancy` function, input validation, event sweep, and result construction. Keep it pure and standard-library-only. (RF-1–RF-9) |
| `tests/test_occupancy.py` | Create | Verify acceptance criteria, boundary cases, invalid inputs, determinism, and tie-breaking. (RF-1–RF-9) |
| `README.md` | Existing; update when implementing | Describe the calculation and its Python API, without suggesting a JSON or CLI contract. (RF-1–RF-5) |
| `ANALYSIS.md` | Create | Explain the algorithm, time and space complexity, decisions, and edge-case analysis in English, as required by the constitution. (RF-1–RF-9) |

No additional runtime packages are proposed. `pytest` is for tests only; the
algorithm itself uses only the standard library. No command-line interface,
service, persistence layer, or external input adapter is proposed. (RF-1–RF-9;
out of scope)

## 3. Input and output model

The public Python API is exactly:

```python
def max_occupancy(
    bookings: list[tuple[int, int]],
) -> tuple[int, int | None, int | None]:
    ...
```

Each booking is a pair `(start, end)` describing the semi-open interval
`[start, end)`. Start and end must be integers, but booleans are invalid even
though `bool` is an `int` subclass in Python. A booking is valid only when
`start < end`. Negative integer endpoints are valid when these conditions hold.
Each input entry is independent; identical entries are not silently merged or
discarded. (RF-2, RF-5, RF-7–RF-9)

For valid non-empty input, the function returns
`(maximum_occupancy, peak_start, peak_end)`, where the last two values delimit
the first chronological continuous period at the global maximum. For empty
input it returns `(0, None, None)`. If any booking is invalid, the whole
calculation fails with an explicit error identifying that booking and the
reason. (RF-1, RF-3–RF-5)

Illustrative Python input and result:

```python
bookings = [(-2, 2), (0, 1), (5, 8), (6, 7)]
result = (2, 0, 1)
```

Illustrative JSON-shaped representation:

```json
{
  "bookings": [
    {"start": -2, "end": 2},
    {"start": 0, "end": 1},
    {"start": 5, "end": 8},
    {"start": 6, "end": 7}
  ],
  "result": {
    "maximum_occupancy": 2,
    "peak_start": 0,
    "peak_end": 1
  }
}
```

The JSON-shaped example is explanatory only. It does not define a JSON
interface, serialization format, or change the Python function contract.
(RF-1, RF-3)

## 4. Calculation outline

Use a sweep line over booking start/end events. Validate the complete input
before calculating a result, so an invalid booking rejects the entire input
instead of returning a partial calculation. (RF-5)

Pseudocode:

```text
function max_occupancy(bookings):
    validate each booking:
        require exactly two endpoints
        require each endpoint to be an integer and not a boolean
        require start < end
        otherwise raise an explicit error identifying the booking and reason

    if bookings is empty:
        return (0, None, None)

    events = []
    for each booking (start, end):
        add (start, START) to events
        add (end, END) to events

    sort events by timestamp, with START before END at equal timestamps
    timestamps = the distinct event timestamps in ascending order
    active = 0
    best = 0
    peak_start = unset
    peak_end = unset

    for each timestamp t, with next distinct timestamp next_t:
        process all START events at t, then all END events at t
        # Evaluate occupancy only after the complete timestamp group.
        # It applies to the positive-duration interval [t, next_t).
        if there is no next_t:
            continue

        if active > best:
            best = active
            peak_start = t
            peak_end = next_t
        else if active == best and active > 0:
            if t == peak_end:
                # The maximum continued through this change instant.
                peak_end = next_t
            # Otherwise retain the earlier, separated maximum period.

    return (best, peak_start, peak_end)
```

The ordering is deterministic: start events precede end events at a shared
timestamp, as specified. Occupancy is evaluated only after all events at that
timestamp have been processed. This preserves `[start, end)` behavior: bookings
ending at `t` are no longer active in `[t, next_t)`, while bookings starting at
`t` are active there. Events sharing a timestamp cannot create a spurious
zero-duration peak. Duplicate bookings produce their own start and end events
and therefore each contribute independently. (RF-2, RF-6–RF-7)

The sweep considers each interval between distinct event timestamps. A new
strictly higher occupancy replaces the previous candidate peak; an equal
occupancy extends the recorded period only when it is contiguous with that
period. An equal but later separated period does not replace the first one.
This returns one continuous interval for a sustained peak and the first
chronological interval when the maximum is reached more than once. (RF-1, RF-3)

For `n` bookings, validation takes `O(n)`, event creation takes `O(n)`,
sorting `2n` events takes `O(n log n)`, and the sweep takes `O(n)`. Total time
is `O(n log n)` and auxiliary space is `O(n)` for the event list. The input is
not mutated. (RF-1, RF-3, RF-5, non-functional efficiency requirement)

## 5. Python API, validation, and unresolved decisions

Keep the exact signature shown above; do not add parameters, return fields, or
side effects. The function returns the global positive maximum and the bounds
of its first continuous period for non-empty valid input, and `(0, None, None)`
for empty input. It accepts valid negative instants. (RF-1–RF-4, RF-8–RF-9)

Validate all bookings before producing events. Reject a booking with a
malformed endpoint count, a non-integer or boolean endpoint, or `start >= end`.
The error must identify the offending booking and the reason, as required by
the specification; invalid entries are not skipped. (RF-5, RF-8)

Validation errors will use a public `InvalidBookingError` class that subclasses
`ValueError`. Its English message will follow
`Invalid booking at index {index} ({booking!r}): {reason}`, where `index` is
zero-based, `booking` is the offending entry, and `reason` briefly describes
the violated rule. This provides callers with both the entry's position and
value without changing the accepted input formats. (RF-5)

The declared function input type is a list of tuples, but runtime handling of a
non-list outer container or a non-tuple booking is not separately specified.
Do not extend the accepted input shapes or define extra rejection behavior
without clarification. (RF-5)

The project currently has no executable Python module, so there is no existing
entry-point behavior to describe or verify. Do not create a user-facing CLI or
assume `python -m occupancy` is part of the product contract; an implementation
may be imported and exercised by tests only unless the scope is separately
changed. (RF-1–RF-9; out of scope)

## 6. Technical decisions and alternatives

| Decision | Rationale | Alternative not selected | Coverage |
|---|---|---|---|
| Use a sorted event sweep with two events per booking. | It gives `O(n log n)` time and `O(n)` extra space, avoiding pairwise overlap comparisons at `O(n²)`. | Compare every booking with every other booking or sample time points. | RF-1–RF-3 |
| Treat intervals as `[start, end)` and evaluate occupancy after processing all events at each timestamp. | It excludes an ending booking at the end instant, includes a starting booking there, and avoids counting transient same-timestamp states. | Treat both endpoints as inclusive or count intermediate event updates as positive-duration occupancy. | RF-2, RF-6 |
| Sort same-timestamp events with starts before ends, but only measure the occupancy after the complete timestamp group. | It follows the stated deterministic event order while honoring the interval definition. | Allow event ordering to determine a zero-duration occupancy observation. | RF-2, RF-6 |
| Keep separate events for duplicate input entries. | Each duplicate is an independent booking by specification. | Deduplicate or merge identical intervals automatically. | RF-7 |
| Check integer endpoints while explicitly excluding booleans, and allow negative integer instants when `start < end`. | This follows Python's bool/int relationship and the explicitly defined endpoint rules. | Use `isinstance(value, int)` alone, or reject negative instants. | RF-5, RF-8–RF-9 |
| Keep the core as a pure module using the standard library only. | It isolates deterministic calculation and validation from I/O, external services, databases, and interfaces. | Add framework, storage, or transport dependencies to the calculation. | RF-1–RF-9 |
| Raise `InvalidBookingError`, a `ValueError` subclass, with a message containing the zero-based index, `repr` of the invalid booking, and a concise reason. | Callers can catch the specific validation error or its standard `ValueError` base and can identify both the offending entry and cause. | Use an unspecified generic exception or report only the value or position. | RF-5 |

## 7. Test strategy

Tests should call the Python function directly and assert return tuples or
explicit validation errors. They should not require JSON handling, external
services, storage, or CLI behavior. Use only `pytest` as a test dependency; the
algorithm remains standard-library-only. (RF-1–RF-9)

Planned test cases:

| Test case | Expected verification | Coverage |
|---|---|---|
| Empty list | Returns `(0, None, None)`. | RF-4 |
| One valid booking | Maximum is one and the period is exactly the booking interval. | RF-1, RF-3 |
| Overlapping bookings | Returns the maximum concurrent count and bounds of the maximum period. | RF-1–RF-3 |
| Consecutive bookings where one ends as another starts | They do not overlap at that instant; no artificial peak is counted. | RF-2, RF-6 |
| Coincident starts and/or ends | Correct occupancy is measured after the full timestamp group. | RF-2, RF-6 |
| Several event types at the same timestamp | Deterministic handling yields the half-open interval result. | RF-2, RF-6 |
| Duplicate identical bookings | Each entry contributes independently. | RF-1, RF-7 |
| Maximum sustained across event timestamps | Returns one continuous period while occupancy does not drop below the global maximum. | RF-3 |
| Several separated periods with equal maximum | Returns the first period chronologically. | RF-3 |
| Negative valid endpoints | Calculation succeeds when each pair has integer endpoints and `start < end`. | RF-5, RF-9 |
| Start equals end; start exceeds end | The whole input is rejected with an explicit identifying error. | RF-5 |
| Missing or extra booking endpoints | The whole input is rejected with an explicit identifying error. | RF-5 |
| Non-integer endpoint | The whole input is rejected. | RF-5, RF-8 |
| Boolean endpoint | The whole input is rejected despite `bool` being an `int` subclass. | RF-5, RF-8 |
| Invalid booking among valid bookings | No partial result is returned; the invalid booking and reason are identified by the error. | RF-5 |

Error tests must assert the exception and identifying details once the pending
exception/message decision has been made; do not bake an unspecified exception
class or exact message into tests before then. No maximum-size or latency
threshold test is specified. (RF-5; non-functional performance measurement)

## 8. Functional-requirement coverage matrix

| Requirement | Plan sections / decisions | Planned tests |
|---|---|---|
| RF-1 — Calculate maximum occupancy | Sections 2–6: pure public module, event sweep, occupancy counting, complexity. | One booking; overlapping bookings; duplicates; non-empty maximum is positive. |
| RF-2 — Apply `[start, end)` semantics | Sections 3–6: interval model, grouped timestamp processing, half-open behavior. | Consecutive bookings; coincident starts/ends; simultaneous events; overlapping intervals. |
| RF-3 — Report the first maximum period | Sections 1, 3–6: continuous-period tracking, extension, reset on a higher maximum, first-period tie-break. | Single peak period; sustained maximum; separated equal maximum periods. |
| RF-4 — Resolve empty lists | Sections 3, 5, and 6: explicit `(0, None, None)` result. | Empty-list result and no error. |
| RF-5 — Reject invalid inputs | Sections 3, 5, 6, and 7: complete validation, whole-list rejection, pending error representation. | Wrong endpoint count; equal/reversed endpoints; invalid entry among valid entries; identifying explicit error. |
| RF-6 — Define same-instant event ordering | Sections 4 and 6: start-before-end ordering and occupancy evaluation after the timestamp group. | Coincident starts/ends and simultaneous end/start transitions. |
| RF-7 — Define duplicate handling | Sections 3, 4, and 6: independent events per input entry, no automatic deduplication. | Identical duplicate bookings each increment occupancy. |
| RF-8 — Define valid integer semantics | Sections 3, 5, 6, and 7: integer endpoint check with booleans rejected. | Integer success; non-integer and boolean endpoint rejection. |
| RF-9 — Define negative instants | Sections 3, 5, 6, and 7: valid negative endpoints are not a business-rule concern of this function. | Valid negative intervals accepted; invalid ordering still rejected. |
