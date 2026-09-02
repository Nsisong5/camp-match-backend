import pytest

from camp_match.modules.profile.domain.value_objects import (
    ScoutProfileDetails,
    StudentProfileDetails,
)


def test_student_profile_details_budget_validation():
    # Valid
    StudentProfileDetails(budget_min_naira=100, budget_max_naira=200)
    # Valid equal
    StudentProfileDetails(budget_min_naira=100, budget_max_naira=100)
    
    # Invalid min > max
    with pytest.raises(ValueError, match="budget_min_naira must be ≤ budget_max_naira"):
        StudentProfileDetails(budget_min_naira=200, budget_max_naira=100)
        
    # Invalid negative
    with pytest.raises(ValueError, match="budget_min_naira must be non-negative"):
        StudentProfileDetails(budget_min_naira=-1)

def test_scout_profile_details_years_active_validation():
    # Valid
    ScoutProfileDetails(years_active=5)
    
    # Invalid negative
    with pytest.raises(ValueError, match="years_active must be non-negative"):
        ScoutProfileDetails(years_active=-1)
