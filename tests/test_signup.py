"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_signup_success():
    """Test successful signup for a student."""
    # Arrange
    activity_name = "Chess Club"
    email = "testuser@example.com"
    # Reset participants for this test
    activities[activity_name]["participants"] = ["michael@mergington.edu"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert email in activities[activity_name]["participants"]

    # Cleanup
    activities[activity_name]["participants"].remove(email)


def test_signup_duplicate_rejected():
    """Test that duplicate signup for the same email is rejected."""
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@example.com"
    activities[activity_name]["participants"] = []

    # Act - First signup
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Act - Attempt duplicate signup
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]
    assert activities[activity_name]["participants"].count(email) == 1

    # Cleanup
    activities[activity_name]["participants"].remove(email)


def test_signup_invalid_activity_returns_404():
    """Test that signup for non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "testuser@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_missing_email_param():
    """Test that signup without email parameter fails."""
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422  # Unprocessable Entity - missing required param


def test_signup_response_structure():
    """Test that signup response has correct structure."""
    # Arrange
    activity_name = "Tennis Club"
    email = "structure_test@example.com"
    activities[activity_name]["participants"] = []

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert email in data["message"]
    assert activity_name in data["message"]

    # Cleanup
    activities[activity_name]["participants"].remove(email)


def test_signup_multiple_students_same_activity():
    """Test that multiple students can sign up for the same activity."""
    # Arrange
    activity_name = "Drama Club"
    email1 = "student1@example.com"
    email2 = "student2@example.com"
    activities[activity_name]["participants"] = []

    # Act
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert email1 in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == 2

    # Cleanup
    activities[activity_name]["participants"].remove(email1)
    activities[activity_name]["participants"].remove(email2)


def test_signup_with_existing_participants():
    """Test signup when activity already has participants."""
    # Arrange
    activity_name = "Debate Team"
    existing_email = "existing@example.com"
    new_email = "newuser@example.com"
    activities[activity_name]["participants"] = [existing_email]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert existing_email in activities[activity_name]["participants"]
    assert new_email in activities[activity_name]["participants"]

    # Cleanup
    activities[activity_name]["participants"].remove(new_email)
