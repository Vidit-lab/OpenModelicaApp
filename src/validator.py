"""Validation for simulation parameters, based on the model's domain limits."""

MIN_START_TIME = 0
MAX_STOP_TIME = 5


class ValidationError(Exception):
    """Raised when simulation inputs fall outside their domain limits."""


def validate_times(start_str: str, stop_str: str) -> tuple[int, int]:
    """Return (start, stop) as integers, enforcing 0 <= start < stop < 5."""
    try:
        start, stop = int(start_str), int(stop_str)
    except ValueError as exc:
        raise ValidationError("Start and Stop times must be integers.") from exc

    if start < MIN_START_TIME:
        raise ValidationError(f"Start time ({start}) must be at least {MIN_START_TIME}.")
    if start >= stop:
        raise ValidationError(f"Start time ({start}) must be less than Stop time ({stop}).")
    if stop >= MAX_STOP_TIME:
        raise ValidationError(f"Stop time ({stop}) must be less than {MAX_STOP_TIME}.")

    return start, stop


if __name__ == '__main__':
    assert validate_times("0", "4") == (0, 4)

    for bad in [("x", "4"), ("-1", "4"), ("3", "3"), ("4", "2"), ("0", "5"), ("0", "9")]:
        try:
            validate_times(*bad)
        except ValidationError:
            continue
        raise AssertionError(f'{bad} should have been rejected')

    print('ok')
