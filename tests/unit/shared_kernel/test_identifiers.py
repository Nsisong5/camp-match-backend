from uuid import uuid4

import pytest

from camp_match.shared_kernel.domain.identifiers import EntityId


def test_entity_id_uniqueness():
    id1 = EntityId.new()
    id2 = EntityId.new()
    assert id1 != id2
    assert id1.value != id2.value


def test_entity_id_equality():
    val = uuid4()
    id1 = EntityId(val)
    id2 = EntityId(val)
    assert id1 == id2
    assert hash(id1) == hash(id2)


def test_entity_id_from_string():
    val = uuid4()
    s = str(val)
    id1 = EntityId.from_string(s)
    assert str(id1) == s
    assert id1.value == val


def test_entity_id_invalid_string():
    with pytest.raises(ValueError):
        EntityId.from_string("invalid-uuid")
