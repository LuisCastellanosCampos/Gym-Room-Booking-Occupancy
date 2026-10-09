class InvalidBookingError(ValueError):
    pass


def max_occupancy(
    bookings: list[tuple[int, int]],
) -> tuple[int, int | None, int | None]:
    if not bookings:
        return (0, None, None)

    for index, booking in enumerate(bookings):
        if len(booking) != 2:
            raise InvalidBookingError(
                f"Invalid booking at index {index} ({booking!r}): "
                "expected a start and end time"
            )

        start, end = booking
        if start >= end:
            raise InvalidBookingError(
                f"Invalid booking at index {index} ({booking!r}): "
                "start must be less than end"
            )

    raise NotImplementedError("Non-empty bookings are not implemented yet.")
