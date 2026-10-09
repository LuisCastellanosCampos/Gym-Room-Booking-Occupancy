class InvalidBookingError(ValueError):
    pass


def _build_sorted_events(
    bookings: list[tuple[int, int]],
) -> list[tuple[int, str]]:
    events = [
        event
        for start, end in bookings
        for event in ((start, "start"), (end, "end"))
    ]
    events.sort(key=lambda event: (event[0], event[1] != "start"))
    return events


def _maximum_concurrency(
    events: list[tuple[int, str]],
) -> tuple[int, int | None, int | None]:
    active = 0
    maximum = 0
    peak_start = None
    peak_end = None
    event_index = 0

    while event_index < len(events):
        timestamp = events[event_index][0]
        while (
            event_index < len(events)
            and events[event_index][0] == timestamp
        ):
            if events[event_index][1] == "start":
                active += 1
            else:
                active -= 1
            event_index += 1

        if event_index < len(events):
            next_timestamp = events[event_index][0]
            if active > maximum:
                maximum = active
                peak_start = timestamp
                peak_end = next_timestamp
            elif active == maximum and active > 0 and timestamp == peak_end:
                peak_end = next_timestamp

    return (maximum, peak_start, peak_end)


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

    events = _build_sorted_events(bookings)
    return _maximum_concurrency(events)
