def test_analyst_can_access_summary(client, analyst_token):
    res = client.get("/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "net_balance" in data
    assert "total_records" in data


def test_viewer_cannot_access_summary(client, viewer_token):
    res = client.get("/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 403


def test_analyst_can_access_category_breakdown(client, analyst_token):
    res = client.get("/api/v1/dashboard/category-breakdown",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_analyst_can_access_trends(client, analyst_token):
    res = client.get("/api/v1/dashboard/trends",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_analyst_can_access_recent_activity(client, analyst_token):
    res = client.get("/api/v1/dashboard/recent-activity",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_full_dashboard_response_shape(client, analyst_token):
    res = client.get("/api/v1/dashboard",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "category_breakdown" in data
    assert "monthly_trends" in data
    assert "recent_activity" in data


def test_admin_can_access_dashboard(client, admin_token):
    res = client.get("/api/v1/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200


def test_viewer_cannot_access_full_dashboard(client, viewer_token):
    res = client.get("/api/v1/dashboard",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 403


def test_recent_activity_limit_param(client, analyst_token):
    res = client.get("/api/v1/dashboard/recent-activity?limit=3",
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert res.status_code == 200
    assert len(res.json()) <= 3