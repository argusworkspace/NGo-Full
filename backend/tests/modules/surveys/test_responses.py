from app.core.security import create_access_token, hash_password
from app.modules.auth.models import User

SAMPLE_QUESTIONS = [
    {"id": "q1", "question": "School name?", "type": "text", "required": True},
    {"id": "q2", "question": "Has library?", "type": "boolean", "required": True},
    {
        "id": "q3",
        "question": "Gender?",
        "type": "single_choice",
        "required": False,
        "options": [{"id": "opt1", "label": "Male"}, {"id": "opt2", "label": "Female"}],
    },
    {"id": "q4", "question": "Rate your experience", "type": "rating", "required": False},
]


async def _create_and_publish(client, admin_token, auth_headers, questions=SAMPLE_QUESTIONS):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Response Test Survey", "questions": questions},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]
    await client.patch(f"/api/v1/projects/{project_id}/publish", headers=auth_headers(admin_token))
    return project_id


async def test_submit_valid_response(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "ABC School"}, {"questionId": "q2", "answer": True}]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201
    body = resp.json()["data"]
    assert body["projectId"] == project_id


async def test_submit_unknown_question_id_rejected(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "does-not-exist", "answer": "x"}]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "UNKNOWN_QUESTION"


async def test_submit_valid_rating_response(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={
            "answers": [
                {"questionId": "q1", "answer": "ABC School"},
                {"questionId": "q2", "answer": True},
                {"questionId": "q4", "answer": 4},
            ]
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 201


async def test_submit_out_of_range_rating_rejected(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={
            "answers": [
                {"questionId": "q1", "answer": "ABC School"},
                {"questionId": "q2", "answer": True},
                {"questionId": "q4", "answer": 7},
            ]
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 422
    assert resp.json()["error"] == "VALIDATION_ERROR"


async def test_submit_invalid_option_rejected(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={
            "answers": [
                {"questionId": "q1", "answer": "ABC School"},
                {"questionId": "q2", "answer": True},
                {"questionId": "q3", "answer": "not-a-real-option"},
            ]
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 422
    assert resp.json()["error"] == "VALIDATION_ERROR"


async def test_submit_missing_required_answer_rejected(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "ABC School"}]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "MISSING_REQUIRED_ANSWER"


async def test_submit_to_unpublished_project_rejected(client, admin_token, user_token, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Draft Survey", "questions": SAMPLE_QUESTIONS},
        headers=auth_headers(admin_token),
    )
    project_id = create.json()["data"]["id"]

    resp = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "ABC School"}]},
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "PROJECT_NOT_PUBLISHED"


async def test_owner_can_view_own_response(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)
    submit = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "x"}, {"questionId": "q2", "answer": False}]},
        headers=auth_headers(user_token),
    )
    response_id = submit.json()["data"]["id"]

    resp = await client.get(f"/api/v1/responses/{response_id}", headers=auth_headers(user_token))
    assert resp.status_code == 200


async def test_other_user_cannot_view_response(
    client, admin_token, user_token, auth_headers, db_session, normal_user
):
    project_id = await _create_and_publish(client, admin_token, auth_headers)
    submit = await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "x"}, {"questionId": "q2", "answer": False}]},
        headers=auth_headers(user_token),
    )
    response_id = submit.json()["data"]["id"]

    other = User(
        name="Someone Else",
        email="other-response-viewer@example.com",
        hashed_password=hash_password("Other@123"),
        role="VOLUNTEER",
    )
    db_session.add(other)
    await db_session.flush()
    other_token = create_access_token(other.id, other.role)

    resp = await client.get(f"/api/v1/responses/{response_id}", headers=auth_headers(other_token))
    assert resp.status_code == 403


async def test_admin_can_list_responses_user_cannot(client, admin_token, user_token, auth_headers):
    project_id = await _create_and_publish(client, admin_token, auth_headers)
    await client.post(
        f"/api/v1/projects/{project_id}/responses",
        json={"answers": [{"questionId": "q1", "answer": "x"}, {"questionId": "q2", "answer": False}]},
        headers=auth_headers(user_token),
    )

    resp = await client.get(f"/api/v1/projects/{project_id}/responses", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1

    resp = await client.get(f"/api/v1/projects/{project_id}/responses", headers=auth_headers(user_token))
    assert resp.status_code == 403
