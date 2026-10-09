import pytest

from occupancy import InvalidBookingError, _build_sorted_events, max_occupancy


def test_empty_bookings_return_zero_occupancy_without_peak_bounds() -> None:
    assert max_occupancy([]) == (0, None, None)


@pytest.mark.parametrize(
    "booking",
    [
        (1,),
        (1, 2, 3),
    ],
)
def test_booking_without_start_and_end_times_raises_identifying_error(
    booking: tuple[int, ...],
) -> None:
    with pytest.raises(ValueError) as error:
        max_occupancy([(0, 1), booking])

    assert type(error.value).__name__ == "InvalidBookingError"
    assert str(error.value) == (
        f"Invalid booking at index 1 ({booking!r}): "
        "expected a start and end time"
    )


@pytest.mark.parametrize(
    ("booking", "reason"),
    [
        ((2, 2), "start must be less than end"),
        ((3, 1), "start must be less than end"),
    ],
)
def test_booking_with_invalid_order_raises_identifying_error(
    booking: tuple[int, int],
    reason: str,
) -> None:
    with pytest.raises(ValueError) as error:
        max_occupancy([(0, 1), booking])

    assert type(error.value).__name__ == "InvalidBookingError"
    assert str(error.value) == (
        f"Invalid booking at index 1 ({booking!r}): {reason}"
    )


@pytest.mark.parametrize(
    ("booking", "reason"),
    [
        ((1.5, 2), "start time must be an integer"),
        ((1, 2.5), "end time must be an integer"),
        (("1", 2), "start time must be an integer"),
        ((1, "2"), "end time must be an integer"),
        ((True, 2), "start time must not be a boolean"),
        ((1, False), "end time must not be a boolean"),
    ],
)
def test_booking_with_non_integer_or_boolean_time_raises_identifying_error(
    booking: tuple[object, object],
    reason: str,
) -> None:
    with pytest.raises(InvalidBookingError) as error:
        max_occupancy([(0, 1), booking])

    assert str(error.value) == (
        f"Invalid booking at index 1 ({booking!r}): {reason}"
    )


@pytest.mark.parametrize(
    ("bookings", "invalid_index"),
    [
        ([(2, 5), (3, 3), (4, 8)], 1),
        ([(3, 3), (2, 5), (4, 8)], 0),
        ([(2, 5), (4, 8), (3, 3)], 2),
    ],
)
def test_mixed_valid_and_invalid_bookings_reject_the_entire_input(
    bookings: list[tuple[int, int]],
    invalid_index: int,
) -> None:
    invalid_booking = bookings[invalid_index]

    with pytest.raises(InvalidBookingError) as error:
        max_occupancy(bookings)

    assert str(error.value) == (
        f"Invalid booking at index {invalid_index} ({invalid_booking!r}): "
        "start must be less than end"
    )


def test_integer_booking_passes_validation() -> None:
    assert max_occupancy([(1, 2)])[0] == 1


@pytest.mark.parametrize(
    "booking",
    [
        (-3, 2),
        (-5, -1),
        (-2, 4),
    ],
)
def test_valid_booking_with_negative_times_passes_validation(
    booking: tuple[int, int],
) -> None:
    assert max_occupancy([booking])[0] == 1


def test_overlapping_bookings_return_maximum_concurrency() -> None:
    assert max_occupancy([(1, 4), (2, 5), (3, 6)])[0] == 3


def test_identical_bookings_each_contribute_to_occupancy() -> None:
    assert max_occupancy([(1, 3), (1, 3), (1, 3)]) == (3, 1, 3)


def test_consecutive_bookings_do_not_overlap_at_shared_instant() -> None:
    assert max_occupancy([(1, 3), (3, 5)])[0] == 1


def test_all_events_at_shared_instant_are_applied_before_measuring() -> None:
    assert max_occupancy([(0, 2), (2, 5), (2, 4)])[0] == 2


def test_maximum_period_extends_across_change_instants() -> None:
    assert max_occupancy([(1, 5), (2, 3), (3, 4)]) == (2, 2, 4)


def test_first_of_separated_equal_maximum_periods_is_returned() -> None:
    assert max_occupancy([(1, 3), (2, 3), (5, 7), (6, 7)]) == (2, 2, 3)


def test_sorted_events_keep_coincident_starts_and_ends() -> None:
    assert _build_sorted_events(
        [(1, 4), (1, 4), (1, 3), (2, 4)]
    ) == [
        (1, "start"),
        (1, "start"),
        (1, "start"),
        (2, "start"),
        (3, "end"),
        (4, "end"),
        (4, "end"),
        (4, "end"),
    ]


def test_sorted_events_place_starts_before_ends_at_shared_instant() -> None:
    assert _build_sorted_events([(1, 2), (2, 3), (0, 2), (2, 4)]) == [
        (0, "start"),
        (1, "start"),
        (2, "start"),
        (2, "start"),
        (2, "end"),
        (2, "end"),
        (3, "end"),
        (4, "end"),
    ]
