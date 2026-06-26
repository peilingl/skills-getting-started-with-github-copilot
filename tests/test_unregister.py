"""
Tests for DELETE /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_unregister_success():
    """Test successful unregister from an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "student_to_remove@example.com"
    activities[activity_name]["participants"] = [email]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_registered():
    """Test that unregister for non-registered student fails."""
    # Arrange
    activity_name = "Programming Class"
    email = "not_registered@example.com"
    activities[activity_name]["participants"] = []

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_unregister_invalid_activity_returns_404():
    """Test that unregister from non-existent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "testuser@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_missing_email_param():
    """Test that unregister without email parameter fails."""
    # Arrange
    activity_name = "Art Studio"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422  # Unprocessable Entity - missing required param


def test_unregister_response_structure():
    """Test that unregister response has correct structure."""
    # Arrange
    activity_name = "Science Club"
    email = "structure_test@example.com"
    activities[activity_name]["participants"] = [email]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_from_activity_with_multiple_participants():
    """Test unregister when activity has multiple participants."""
    # Arrange
    activity_name = "Gym Class"
    email1 = "participant1@example.com"
    email2 = "participant2@example.com"
    email3 = "participant3@example.com"
    activities[activity_name]["participants"] = [email1, email2, email3]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email2})

    # Assert
    assert response.status_code == 200
    assert email1 in activities[activity_name]["participants"]
    assert email2 not in activities[activity_name]["participants"]
    assert email3 in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == 2

    # Cleanup
    activities[activity_name]["participants"] = [email1, email3]


def test_unregister_then_register_again():
    """Test that a student can register again after unregistering."""
    # Arrange
    activity_name = "Science Club"
    email = "temporary_student@example.com"
    activities[activity_name]["participants"] = []

    # Act - Register first time
    signup_response_1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act - Unregister
    unregister_response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act - Register again
    signup_response_2 = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert signup_response_1.status_code == 200
    assert unregister_response.status_code == 200
    assert signup_response_2.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Cleanup
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def test_unregister_preserves_other_participants():
    """Test that unregistering one student doesn't affect others."""
    # Arrange
    activity_name = "Tennis Club"
    keep_email = "keep_this@example.com"
    remove_email = "remove_this@example.com"
    activities[activity_name]["participants"] = [keep_email, remove_email]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": remove_email})

    # Assert
    assert response.status_code == 200
    assert keep_email in activities[activity_name]["participants"]
    assert remove_email not in activities[activity_name]["participants"]

    # Cleanup
    activities[activity_name]["participants"] = [keep_email]
