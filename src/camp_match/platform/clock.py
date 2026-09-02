from datetime import UTC, datetime


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)

_clock = SystemClock()

def get_clock() -> SystemClock:
    return _clock
