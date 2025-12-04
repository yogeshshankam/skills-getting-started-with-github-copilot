"""
Tests for the Mergington High School FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app
import uuid


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify activities structure
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Verify activity details
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    unique_email = f"student_{uuid.uuid4()}@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={unique_email}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {unique_email}" in data["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert unique_email in activities[activity]["participants"]


def test_signup_duplicate_fails(client):
    """Test that signing up twice fails"""
    unique_email = f"duplicate_{uuid.uuid4()}@mergington.edu"
    activity = "Programming Class"
    
    # First signup should succeed
    response1 = client.post(f"/activities/{activity}/signup?email={unique_email}")
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(f"/activities/{activity}/signup?email={unique_email}")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_invalid_activity(client):
    """Test signup for non-existent activity"""
    response = client.post(f"/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    unique_email = f"unregister_{uuid.uuid4()}@mergington.edu"
    activity = "Soccer Team"
    
    # First, sign up
    response_signup = client.post(f"/activities/{activity}/signup?email={unique_email}")
    assert response_signup.status_code == 200
    
    # Verify participant was added
    activities_before = client.get("/activities").json()
    assert unique_email in activities_before[activity]["participants"]
    
    # Now unregister
    response_unregister = client.post(f"/activities/{activity}/unregister?email={unique_email}")
    assert response_unregister.status_code == 200
    assert "Unregistered" in response_unregister.json()["message"]
    
    # Verify participant was removed
    activities_after = client.get("/activities").json()
    assert unique_email not in activities_after[activity]["participants"]


def test_unregister_not_registered(client):
    """Test unregister for someone not registered"""
    unique_email = f"notregistered_{uuid.uuid4()}@mergington.edu"
    activity = "Drama Club"
    
    response = client.post(f"/activities/{activity}/unregister?email={unique_email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]


def test_unregister_invalid_activity(client):
    """Test unregister from non-existent activity"""
    response = client.post(f"/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_activities_data_integrity(client):
    """Test that activities data is intact and accessible"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Drama Club",
        "Art Workshop",
        "Math Olympiad",
        "Science Club"
    ]
    
    for activity in expected_activities:
        assert activity in activities
        assert activities[activity]["max_participants"] > 0
        assert isinstance(activities[activity]["participants"], list)
