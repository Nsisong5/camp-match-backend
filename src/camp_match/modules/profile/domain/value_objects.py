from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class ProfileType(Enum):
    STUDENT = "STUDENT"
    SCOUT = "SCOUT"

class AccommodationTypePreference(Enum):
    SELF_CONTAINED = "SELF_CONTAINED"
    SHARED_ROOM = "SHARED_ROOM"
    HOSTEL = "HOSTEL"
    NO_PREFERENCE = "NO_PREFERENCE"

class CleanlinessPreference(Enum):
    VERY_TIDY = "VERY_TIDY"
    MODERATE = "MODERATE"
    RELAXED = "RELAXED"

class SleepSchedule(Enum):
    EARLY_BIRD = "EARLY_BIRD"
    NIGHT_OWL = "NIGHT_OWL"
    FLEXIBLE = "FLEXIBLE"

class ScoutAvailabilityStatus(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"

@dataclass(frozen=True)
class StudentProfileDetails:
    university_name: str | None = None
    department: str | None = None
    budget_min_naira: int | None = None
    budget_max_naira: int | None = None
    preferred_accommodation_type: AccommodationTypePreference | None = None
    cleanliness_preference: CleanlinessPreference | None = None
    sleep_schedule: SleepSchedule | None = None

    def __post_init__(self) -> None:
        if self.budget_min_naira is not None and self.budget_min_naira < 0:
            raise ValueError("budget_min_naira must be non-negative")
        if self.budget_max_naira is not None and self.budget_max_naira < 0:
            raise ValueError("budget_max_naira must be non-negative")
        if (
            self.budget_min_naira is not None 
            and self.budget_max_naira is not None 
            and self.budget_min_naira > self.budget_max_naira
        ):
            raise ValueError("budget_min_naira must be ≤ budget_max_naira")
    
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data

@dataclass(frozen=True)
class ScoutProfileDetails:
    business_name: str | None = None
    business_description: str | None = None
    years_active: int | None = None
    availability_status: ScoutAvailabilityStatus = ScoutAvailabilityStatus.ACTIVE

    def __post_init__(self) -> None:
        if self.years_active is not None and self.years_active < 0:
            raise ValueError("years_active must be non-negative")
    
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data
