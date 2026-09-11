from camp_match.modules.university_location.domain.entities import Campus, University
from camp_match.modules.university_location.domain.value_objects import (
    Coordinates,
    InstitutionType,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


def test_university_normalization():
    uni = University(
        id=EntityId.new(),
        official_name="  University   of   Lagos  ",
        institution_type=InstitutionType.UNIVERSITY,
    )
    assert uni.official_name == "University of Lagos"
    assert uni.normalized_name == "university of lagos"


def test_campus_normalization():
    campus = Campus(
        id=EntityId.new(),
        university_id=EntityId.new(),
        name="  Main   Campus  ",
        coordinates=Coordinates(latitude=6.5244, longitude=3.3792),
    )
    assert campus.name == "Main Campus"
    assert campus.normalized_name == "main campus"


def test_immutable_ids():
    uni_id = EntityId.new()
    uni = University(
        id=uni_id,
        official_name="Unilag",
        institution_type=InstitutionType.UNIVERSITY,
    )
    assert uni.id == uni_id

    campus_id = EntityId.new()
    uni_id_for_campus = EntityId.new()
    campus = Campus(
        id=campus_id,
        university_id=uni_id_for_campus,
        name="Main",
        coordinates=Coordinates(latitude=0.0, longitude=0.0),
    )
    assert campus.id == campus_id
    assert campus.university_id == uni_id_for_campus
    # No way to change id or university_id is enforced by not having public setters
    # and no update methods accepting them.
