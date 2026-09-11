import pytest

from camp_match.modules.university_location.domain.value_objects import Coordinates


def test_valid_coordinates_construct():
    coords = Coordinates(latitude=6.5244, longitude=3.3792)
    assert coords.latitude == 6.5244
    assert coords.longitude == 3.3792


def test_latitude_outside_range_raises_value_error():
    with pytest.raises(ValueError, match="latitude must be between -90 and 90 inclusive"):
        Coordinates(latitude=90.1, longitude=3.3792)

    with pytest.raises(ValueError, match="latitude must be between -90 and 90 inclusive"):
        Coordinates(latitude=-90.1, longitude=3.3792)


def test_longitude_outside_range_raises_value_error():
    with pytest.raises(ValueError, match="longitude must be between -180 and 180 inclusive"):
        Coordinates(latitude=6.5244, longitude=180.1)

    with pytest.raises(ValueError, match="longitude must be between -180 and 180 inclusive"):
        Coordinates(latitude=6.5244, longitude=-180.1)


def test_boundary_values_are_valid():
    # Boundary +90, +180
    coords1 = Coordinates(latitude=90.0, longitude=180.0)
    assert coords1.latitude == 90.0
    assert coords1.longitude == 180.0

    # Boundary -90, -180
    coords2 = Coordinates(latitude=-90.0, longitude=-180.0)
    assert coords2.latitude == -90.0
    assert coords2.longitude == -180.0
