from datetime import UTC, datetime

import pytest

from camp_match.platform.clock import SystemClock
from tests.support.fixed_clock import FixedClock


@pytest.mark.unit
def test_system_clock_now():
    clock = SystemClock()
    time1 = clock.now()

    assert time1.tzinfo is not None
    assert time1.tzinfo == UTC


@pytest.mark.unit
def test_fixed_clock_now():
    fixed_time = datetime(2026, 8, 14, 12, 0, 0, tzinfo=UTC)
    clock = FixedClock(fixed_time)

    assert clock.now() == fixed_time
