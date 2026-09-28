from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from camp_match.modules.profile.domain.value_objects import (
    AccommodationTypePreference,
    CleanlinessPreference,
    ProfileType,
    ScoutAvailabilityStatus,
    SleepSchedule,
)
from camp_match.platform.db.base import Base


class ProfileModel(Base):
    __tablename__ = "profiles"
    id = Column(UUID(as_uuid=True), primary_key=True)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identity_accounts.id"), unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    avatar_media_id = Column(UUID(as_uuid=True), nullable=True)
    profile_type = Column(SQLEnum(ProfileType), nullable=False)

class StudentProfileModel(Base):
    __tablename__ = "student_profiles"
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), primary_key=True)
    university_name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    budget_min_naira = Column(Integer, nullable=True)
    budget_max_naira = Column(Integer, nullable=True)
    preferred_accommodation_type = Column(SQLEnum(AccommodationTypePreference), nullable=True)
    cleanliness_preference = Column(SQLEnum(CleanlinessPreference), nullable=True)
    sleep_schedule = Column(SQLEnum(SleepSchedule), nullable=True)

class ScoutProfileModel(Base):
    __tablename__ = "scout_profiles"
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), primary_key=True)
    business_name = Column(String, nullable=True)
    business_description = Column(String, nullable=True)
    years_active = Column(Integer, nullable=True)
    availability_status = Column(SQLEnum(ScoutAvailabilityStatus), nullable=False, default=ScoutAvailabilityStatus.ACTIVE)
