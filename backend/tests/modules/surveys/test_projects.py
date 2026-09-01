SAMPLE_QUESTIONS = [
    {"id": "q1", "question": "School name?", "type": "text", "required": True},
    {"id": "q2", "question": "Has library?", "type": "boolean", "required": True},
    {
        "id": "q3",
        "question": "Gender?",
        "type": "single_choice",
        "required": True,
        "options": [{"id": "opt1", "label": "Male"}, {"id": "opt2", "label": "Female"}],
    },
]


async def test_admin_creates_project(client, admin_token, auth_headers):
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "Test Survey", "description": "d", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
    body = resp.json()["data"]
    assert body["status"] == "DRAFT"
    assert len(body["questions"]) == 3
    assert body["responseCount"] == 0


async def test_user_cannot_create_project(client, user_token, auth_headers):
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "Nope", "questions": []},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 403


async def test_user_cannot_publish_project(client, admin_token, user_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project_id}/publish", headers=auth_headers(user_token)
    )
    assert resp.status_code == 403


async def test_user_cannot_modify_questions(client, admin_token, user_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Hacked", "questions": []},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 403


async def test_get_projects_list_filters_by_role(client, admin_token, user_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Draft Only", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.get("/api/v1/projects", headers=auth_headers(user_token))
    assert resp.status_code == 200
    assert all(p["id"] != project_id for p in resp.json()["data"])

    resp = await client.get("/api/v1/projects", headers=auth_headers(admin_token))
    assert any(p["id"] == project_id for p in resp.json()["data"])


async def test_publish_and_archive_flow(client, admin_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.patch(f"/api/v1/projects/{project_id}/publish", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "PUBLISHED"

    resp = await client.patch(f"/api/v1/projects/{project_id}/archive", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ARCHIVED"


async def test_get_project_by_id(client, admin_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == project_id


async def test_response_count_reflects_submissions(client, admin_token, user_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Counted Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]
    await client.patch(f"/api/v1/projects/{project_id}/publish", headers=auth_headers(admin_token))

    await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={
            "answers": [
                {"questionId": "q1", "answer": "x"},
                {"questionId": "q2", "answer": True},
                {"questionId": "q3", "answer": "opt1"},
            ]
        },
        headers=auth_headers(user_token),
    )

    resp = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers(admin_token))
    assert resp.json()["data"]["responseCount"] == 1

    resp = await client.get("/api/v1/projects", headers=auth_headers(admin_token))
    listed = next(p for p in resp.json()["data"] if p["id"] == project_id)
    assert listed["responseCount"] == 1
