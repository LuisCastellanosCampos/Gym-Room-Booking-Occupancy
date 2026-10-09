import pytest

from occupancy import InvalidBookingError, max_occupancy


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


def test_integer_booking_passes_validation() -> None:
    with pytest.raises(
        NotImplementedError,
        match="Non-empty bookings are not implemented yet",
    ):
        max_occupancy([(1, 2)])
