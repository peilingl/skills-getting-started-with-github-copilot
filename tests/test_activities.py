"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities_returns_all_activities():
    """Test that GET /activities returns all 9 activities."""
    # Arrange
    expected_activity_count = 9

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == expected_activity_count
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Basketball Team" in activities
    assert "Tennis Club" in activities
    assert "Art Studio" in activities
    assert "Drama Club" in activities
    assert "Debate Team" in activities
    assert "Science Club" in activities


def test_activities_response_structure():
    """Test that each activity has the correct response structure."""
    # Arrange
    required_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
        assert required_keys == set(activity_data.keys()), \
            f"{activity_name} missing required keys. Expected {required_keys}, got {set(activity_data.keys())}"
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_activities_response_contains_participants():
    """Test that activities response includes participant information."""
    # Arrange
    # Chess Club should have initial participants

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) > 0
    assert all(isinstance(email, str) for email in chess_club["participants"])


def test_activities_have_max_participants():
    """Test that all activities have valid max_participants values."""
    # Arrange
    expected_min_capacity = 1

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        assert activity_data["max_participants"] >= expected_min_capacity, \
            f"{activity_name} has invalid max_participants: {activity_data['max_participants']}"
