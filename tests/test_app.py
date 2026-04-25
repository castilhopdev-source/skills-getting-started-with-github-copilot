import copy

from fastapi.testclient import TestClient

from src.app import app, activities as activities_store

client = TestClient(app)
_original_activities = copy.deepcopy(activities_store)


def setup_function(function):
    activities_store.clear()
    activities_store.update(copy.deepcopy(_original_activities))


def teardown_function(function):
    activities_store.clear()
    activities_store.update(copy.deepcopy(_original_activities))


def test_get_activities_returns_known_activity():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Already signed up"


def test_remove_participant():
    email = "daniel@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    email = "missing@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
