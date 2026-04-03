import pytest


@pytest.fixture(scope="module")
def created_record_id(client, analyst_token):
    res = client.post("/api/v1/records",
        json={
            "amount": 1500.00,
            "type": "INCOME",
            "category": "TestCategory",
            "date": "2025-01-15",
            "notes": "Test income record"
        },
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_analyst_can_create_record(client, analyst_token):
    res = client.post("/api/v1/records",
        json={
            "amount": 200.00,
            "type": "EXPENSE",
            "category": "TestCategory",
            "date": "2025-01-20",
            "notes": "Test expense"
        },
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["amount"] == "200.00"
    assert data["type"] == "EXPENSE"


def test_viewer_cannot_create_record(client, viewer_token):
    res = client.post("/api/v1/records",
        json={
            "amount": 100.00,
            "type": "INCOME",
            "category": "TestCategory",
            "date": "2025-01-10"
        },
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 403


def test_create_record_negative_amount(client, analyst_token):
    res = client.post("/api/v1/records",
        json={
            "amount": -500.00,
            "type": "INCOME",
            "category": "TestCategory",
            "date": "2025-01-10"
        },
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 422


def test_viewer_can_list_records(client, viewer_token):
    res = client.get("/api/v1/records",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 200
    assert "data" in res.json()
    assert "meta" in res.json()


def test_list_records_with_type_filter(client, viewer_token):
    res = client.get("/api/v1/records?type=INCOME",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 200
    for record in res.json()["data"]:
        assert record["type"] == "INCOME"


def test_list_records_pagination(client, viewer_token):
    res = client.get("/api/v1/records?page=1&limit=2",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 200
    meta = res.json()["meta"]
    assert meta["page"] == 1
    assert meta["limit"] == 2
    assert len(res.json()["data"]) <= 2


def test_get_record_by_id(client, viewer_token, created_record_id):
    res = client.get(f"/api/v1/records/{created_record_id}",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 200
    assert res.json()["id"] == created_record_id


def test_get_nonexistent_record(client, viewer_token):
    res = client.get("/api/v1/records/999999",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 404


def test_admin_can_update_record(client, admin_token, created_record_id):
    res = client.put(f"/api/v1/records/{created_record_id}",
        json={"notes": "Updated by admin"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["notes"] == "Updated by admin"


def test_analyst_cannot_update_record(client, analyst_token, created_record_id):
    res = client.put(f"/api/v1/records/{created_record_id}",
        json={"notes": "Analyst trying to update"},
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 403


def test_admin_can_soft_delete_record(client, admin_token, created_record_id):
    res = client.delete(f"/api/v1/records/{created_record_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 204

    # Deleted record should no longer appear
    get_res = client.get(f"/api/v1/records/{created_record_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_res.status_code == 404


def test_viewer_cannot_delete_record(client, viewer_token, created_record_id):
    res = client.delete(f"/api/v1/records/{created_record_id}",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 403