# Specification: maximum concurrent occupancy calculation

## Context and objective

A set of room bookings may overlap in time. We need to determine the highest
number of bookings that are active at the same time and the first period in
which that maximum occupancy is reached.

The objective of the MVP is to provide a correct, efficient and predictable
calculation for large booking lists. The result must identify the maximum
occupancy, the instant at which the first period reaching that maximum begins,
and the instant at which that period ends. The solution must be understandable
and maintainable by a junior developer.

## Users

- A consumer or system that needs to know the peak occupancy of a set of bookings.
- A developer who integrates or maintains the calculation and needs
  unambiguous results for valid, empty and invalid inputs.

## User stories

- As a consumer, I want to know the maximum number of simultaneous bookings so
  that I can size the occupancy of a room.
- As a consumer, I want to know when the first period with that maximum starts
  and ends so that I can identify the interval of highest demand.
- As a consumer, I want a defined result for an empty list and an explicit error
  for invalid inputs so that I can distinguish these cases without implicit
  interpretation.
- As a developer, I want clear overlap and tie-break rules so that I can
  maintain and verify the behavior.

## Result contract

The calculation must return a 3-item ordered tuple:

- first item: the global maximum occupancy
- second item: the start instant of the first chronological period that reaches
  that maximum
- third item: the end instant of that same period

The result contract is:

- valid non-empty input: `(maximum_occupancy, start_of_first_peak, end_of_first_peak)`
- empty input: `(0, None, None)`
- invalid input: the function fails by raising an explicit error that identifies
  the invalid booking and the reason it is invalid

## Functional requirements

### RF-1: Calculate the maximum occupancy

The system shall determine the largest number of bookings that are active at the
same time for a valid list of bookings.

**Acceptance criteria (EARS):**

- When it receives a valid non-empty list, the system shall return the largest
  number of concurrent bookings at any instant covered by the bookings.
- When at least one valid booking exists, the maximum occupancy shall be greater
  than zero.

### RF-2: Apply the interval semantics

The system shall interpret each booking as active from its start instant,
inclusive, to its end instant, exclusive.

**Acceptance criteria (EARS):**

- When a booking ends at the same instant another begins, the system shall not
  count them as overlapping at that instant.
- When two bookings share any positive-length interval of time, both shall
  contribute to the concurrent occupancy during that interval.

### RF-3: Report the maximum period

The system shall return the start and end instants of the first chronological
period in which the global maximum occupancy is reached. The period begins when
occupancy reaches that maximum and ends when occupancy drops below it.

**Acceptance criteria (EARS):**

- When the maximum occupancy occurs in a single period, the system shall return
  the start and end of that period.
- When the maximum occupancy occurs in several separated periods, the system
  shall return the start and end of the first chronological period.
- When occupancy remains at the maximum across change instants that do not make
  it fall below that maximum, the system shall report a single continuous period.

### RF-4: Resolve empty lists

The system shall represent the absence of bookings explicitly.

**Acceptance criteria (EARS):**

- When it receives an empty list, the system shall return a maximum occupancy of
  zero and leave the peak start and peak end values unset.
- An empty list shall be considered valid and shall not be rejected as invalid.

### RF-5: Reject invalid inputs

The system shall reject the entire list if any booking fails the validity rules.

**Acceptance criteria (EARS):**

- When a booking does not contain exactly two integer values, the system shall
  reject the entire input and raise an explicit error.
- When the start of a booking is equal to or later than its end, the system
  shall reject the entire input and raise an explicit error.
- When all bookings are valid, the system shall not reject them merely because
  one or more instants are negative.
- Boolean values are not valid integer endpoints for this calculation.

### RF-6: Define event ordering at the same instant

The system shall process same-instant events deterministically.

**Acceptance criteria (EARS):**

- When several bookings begin or end at the same instant, the system shall
  process starts before ends.
- This ordering ensures that a booking ending at time `t` and another beginning
  at time `t` are not considered overlapping at time `t`.

### RF-7: Define duplicate handling

The system shall treat duplicate bookings as independent entries unless the
input is explicitly deduplicated before the calculation.

**Acceptance criteria (EARS):**

- Identical bookings appearing as distinct entries shall each contribute to the
  occupancy count according to the interval semantics.
- The system shall not merge or drop duplicate bookings automatically.

### RF-8: Define valid integer semantics

The system shall accept integer values as valid endpoints and shall reject
non-integer and boolean values.

**Acceptance criteria (EARS):**

- Integer values are valid endpoints.
- Non-integer values are invalid.
- Boolean values are invalid even though Python treats them as integers.

### RF-9: Define negative instants

The system shall accept negative integer instants when the booking itself is
valid.

**Acceptance criteria (EARS):**

- A negative start or end value is valid when both are integers and the start is
  strictly smaller than the end.
- Business rules concerning disallowed time ranges or negative values, if any,
  must be enforced before this calculation is requested.

## Non-functional requirements

- **Efficiency:** the calculation shall scale efficiently as the number of
  bookings grows and shall avoid unnecessary work that would prevent large lists
  from being handled well.
- **Maintainability:** the overlap rules, period selection and validation shall
  be clear and consistent for a junior developer.
- **Determinism:** the same valid list shall always produce the same result,
  according to the defined tie-break rules.
- **Independence from external business rules:** the calculation shall accept
  negative integer instants; any restrictions on allowed clock ranges or
  negative instants must be applied before requesting the calculation.
- **Performance measurement:** the MVP does not set a maximum booking count or a
  target latency value. Efficiency will be assessed qualitatively until such
  thresholds are agreed.

## Boundary cases

- Empty list: maximum occupancy equal to zero, with no peak start and no peak end.
- One valid booking: occupancy is one throughout the booking duration.
- Consecutive bookings whose end equals the next start: they do not overlap at
  that instant.
- Bookings with coincident starts or ends: occupancy reflects which bookings are
  active according to the inclusive/exclusive end semantics.
- Several separated periods with the same maximum occupancy: the first one in
  chronological order is reported.
- Start equal to end, start greater than end, non-integer endpoints, boolean
  endpoints, or a booking not containing exactly two endpoints: the entire list
  is rejected.
- Negative instants: accepted when all endpoints are valid integers and the
  start is lower than the end.
- Duplicate identical bookings: each entry contributes independently unless the
  caller deduplicates before the calculation.

## Out of scope

- Applying business rules about clock hours, permitted ranges or disallowed
  negative instants.
- Receiving bookings from interfaces, external services or storage.
- Creating, modifying, cancelling or persisting bookings.
- Calculating metrics other than the maximum occupancy and the first period in
  which it is reached.
- Defining a maximum booking count or a numeric response-time goal.

## Completion criteria

- All functional requirements have verifiable acceptance criteria.
- Endpoint semantics, tie-break behavior, empty lists and invalid inputs are
  consistent with this specification.
- The boundary cases listed above have been verified, including inputs with
  multiple equal peak periods.
- The calculation demonstrates efficient behavior as booking counts increase,
  without depending on a numeric threshold not yet agreed.
- The resulting documentation allows a junior developer to understand the
  expected behavior without implicit decisions.

## Open decisions resolved by this version

The following points are now explicitly decided in this specification:

- The return contract is an ordered tuple: `(maximum_occupancy, peak_start, peak_end)`.
- Empty input returns `(0, None, None)`.
- Invalid input raises an explicit error that identifies the offending booking
  and the reason for rejection.
- Booking intervals are semi-open: `[start, end)`.
- Same-instant events are processed with starts before ends.
- A peak period is a continuous interval during which occupancy equals the global
  maximum.
- Duplicate entries are treated as independent if they are present as distinct
  bookings.
- Boolean values are rejected as invalid integer endpoints.
- Negative integer instants are accepted when valid by the rules above.
- The specification language and technical terminology are English to align with
  the project constitution.
