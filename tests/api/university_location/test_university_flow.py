import pytest
from fastapi import status
from camp_match.modules.security.domain.value_objects import Role
from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.shared_kernel.domain.identifiers import EntityId

@pytest.mark.asyncio
async def test_university_campus_flow(client, db_session):
    # 1. Setup Admin User
    # Register
    reg_resp = await client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "password123"})
    assert reg_resp.status_code == 201
    admin_id = reg_resp.json()["id"]

    # Assign ADMIN role
    role_repo = SqlAlchemyRoleRepository(db_session)
    await role_repo.assign_role(EntityId.from_string(admin_id), Role.ADMIN)
    await db_session.commit()

    # Login
    login_resp = await client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create University
    uni_data = {
        "official_name": "University of Lagos",
        "institution_type": "UNIVERSITY",
        "state_region": "Lagos"
    }
    create_uni_resp = await client.post("/api/v1/universities", json=uni_data, headers=headers)
    assert create_uni_resp.status_code == 201
    uni_id = create_uni_resp.json()["id"]

    # 3. Create two campuses under it, one flagged is_main_campus
    campus1_payload = {
        "name": "Akoka Main",
        "latitude": 6.5157,
        "longitude": 3.3897,
        "is_main_campus": True
    }
    campus2_payload = {
        "name": "Idi-Araba",
        "latitude": 6.5244,
        "longitude": 3.3792,
        "is_main_campus": False
    }
    
    c1_resp = await client.post(f"/api/v1/universities/{uni_id}/campuses", json=campus1_payload, headers=headers)
    assert c1_resp.status_code == 201
    c1_id = c1_resp.json()["id"]
    
    c2_resp = await client.post(f"/api/v1/universities/{uni_id}/campuses", json=campus2_payload, headers=headers)
    assert c2_resp.status_code == 201
    c2_id = c2_resp.json()["id"]

    # 4. Confirm listing campuses for that university returns both
    list_resp = await client.get(f"/api/v1/universities/{uni_id}/campuses", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) == 2
    campus_ids = [i["id"] for i in items]
    assert c1_id in campus_ids
    assert c2_id in campus_ids

    # 5. Deactivate the university via PATCH
    update_uni_resp = await client.patch(f"/api/v1/universities/{uni_id}", json={"status": "INACTIVE"}, headers=headers)
    assert update_uni_resp.status_code == 200
    assert update_uni_resp.json()["status"] == "INACTIVE"

    # 6. Confirm a direct GET on either campus still resolves (ADR-046)
    get_c1_resp = await client.get(f"/api/v1/campuses/{c1_id}", headers=headers)
    assert get_c1_resp.status_code == 200
    assert get_c1_resp.json()["id"] == c1_id

    # 7. Confirm the campus list for that university now returns empty by default (active/active rule)
    list_after_deactivation_resp = await client.get(f"/api/v1/universities/{uni_id}/campuses", headers=headers)
    assert list_after_deactivation_resp.status_code == 200
    assert len(list_after_deactivation_resp.json()["items"]) == 0

    # 8. Confirm passing an explicit "include inactive" flag on the list surfaces them again
    list_with_inactive_resp = await client.get(f"/api/v1/universities/{uni_id}/campuses?include_inactive=true", headers=headers)
    assert list_with_inactive_resp.status_code == 200
    assert len(list_with_inactive_resp.json()["items"]) == 2

    # 9. Error scenarios
    # creating a campus under a nonexistent university returns 404
    bad_uni_id = str(EntityId.new())
    bad_campus_resp = await client.post(f"/api/v1/universities/{bad_uni_id}/campuses", json=campus1_payload, headers=headers)
    assert bad_campus_resp.status_code == 404
    
    # under an inactive one returns 422 inactive_institution (as uni_id is currently inactive)
    inactive_campus_resp = await client.post(f"/api/v1/universities/{uni_id}/campuses", json=campus1_payload, headers=headers)
    assert inactive_campus_resp.status_code == 422
    assert inactive_campus_resp.json()["error"]["code"] == "inactive_institution"
    
    # duplicate university name returns 409
    dup_uni_resp = await client.post("/api/v1/universities", json=uni_data, headers=headers)
    assert dup_uni_resp.status_code == 409
    
    # Need an active university first for the remaining tests
    active_uni_resp = await client.post("/api/v1/universities", json={**uni_data, "official_name": "Active Uni"}, headers=headers)
    active_uni_id = active_uni_resp.json()["id"]
    
    # out-of-range coordinates return 422 
    bad_coords_payload = {**campus1_payload, "latitude": 100.0}
    bad_coords_resp = await client.post(f"/api/v1/universities/{active_uni_id}/campuses", json=bad_coords_payload, headers=headers)
    assert bad_coords_resp.status_code == 422
    assert "detail" in bad_coords_resp.json()
    assert bad_coords_resp.json()["detail"][0]["msg"] == 'Input should be less than or equal to 90'
    
    # attempting to flag a second campus as is_main_campus for the same university fails
    # Create the first main campus
    await client.post(f"/api/v1/universities/{active_uni_id}/campuses", json={**campus1_payload, "is_main_campus": True}, headers=headers)
    
    # Try to create a second main campus
    second_main_resp = await client.post(f"/api/v1/universities/{active_uni_id}/campuses", json={**campus2_payload, "is_main_campus": True}, headers=headers)
    # ADR-045 says "Any attempt to create/flag a second main campus ... MUST be rejected"
    assert second_main_resp.status_code in (409, 422)
