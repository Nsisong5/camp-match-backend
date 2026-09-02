import pytest

from camp_match.modules.profile.domain.entities import Profile
from camp_match.modules.profile.domain.value_objects import (
    ProfileType,
    ScoutProfileDetails,
    StudentProfileDetails,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


def test_profile_creation_student():
    student_details = StudentProfileDetails(university_name="Uni")
    profile = Profile(
        id=EntityId.new(),
        identity_id=EntityId.new(),
        display_name="Student",
        student_details=student_details,
    )
    assert profile.profile_type == ProfileType.STUDENT
    assert profile.student_details == student_details
    assert profile.scout_details is None

def test_profile_creation_scout():
    scout_details = ScoutProfileDetails(business_name="Biz")
    profile = Profile(
        id=EntityId.new(),
        identity_id=EntityId.new(),
        display_name="Scout",
        scout_details=scout_details,
    )
    assert profile.profile_type == ProfileType.SCOUT
    assert profile.scout_details == scout_details
    assert profile.student_details is None

def test_profile_creation_invalid_details():
    with pytest.raises(ValueError, match="Exactly one of student_details or scout_details must be provided"):
        Profile(
            id=EntityId.new(),
            identity_id=EntityId.new(),
            display_name="Invalid",
        )
    
    with pytest.raises(ValueError, match="Exactly one of student_details or scout_details must be provided"):
        Profile(
            id=EntityId.new(),
            identity_id=EntityId.new(),
            display_name="Invalid",
            student_details=StudentProfileDetails(),
            scout_details=ScoutProfileDetails(),
        )

def test_profile_update_core():
    profile = Profile(
        id=EntityId.new(),
        identity_id=EntityId.new(),
        display_name="Old Name",
        student_details=StudentProfileDetails(),
    )
    profile.update_core(display_name="New Name", bio="New Bio")
    assert profile.display_name == "New Name"
    assert profile.bio == "New Bio"
