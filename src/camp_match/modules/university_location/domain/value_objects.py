from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class InstitutionType(Enum):
    UNIVERSITY = "UNIVERSITY"
    POLYTECHNIC = "POLYTECHNIC"
    COLLEGE_OF_EDUCATION = "COLLEGE_OF_EDUCATION"
    OTHER = "OTHER"


class InstitutionStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError("latitude must be between -90 and 90 inclusive")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("longitude must be between -180 and 180 inclusive")


def clean_name(raw: str) -> str:
    """Trim and collapse internal whitespace to single spaces, preserving casing."""
    return re.sub(r"\s+", " ", raw.strip())


def normalize_name(raw: str) -> str:
    """Trim, lowercase, and collapse internal whitespace to single spaces."""
    return clean_name(raw).lower()
