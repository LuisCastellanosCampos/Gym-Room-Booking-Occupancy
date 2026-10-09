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
        for time_name, time_value in (("start", start), ("end", end)):
            if isinstance(time_value, bool):
                raise InvalidBookingError(
                    f"Invalid booking at index {index} ({booking!r}): "
                    f"{time_name} time must not be a boolean"
                )
            if not isinstance(time_value, int):
                raise InvalidBookingError(
                    f"Invalid booking at index {index} ({booking!r}): "
                    f"{time_name} time must be an integer"
                )

        if start >= end:
            raise InvalidBookingError(
                f"Invalid booking at index {index} ({booking!r}): "
                "start must be less than end"
            )

    raise NotImplementedError("Non-empty bookings are not implemented yet.")
