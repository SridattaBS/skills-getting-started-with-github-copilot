"""
Comprehensive AAA-style tests for the activities API endpoints
"""

import pytest
from urllib.parse import quote


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Swimming Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == len(expected_activities)
        for name in expected_activities:
            assert name in activities_data

    def test_get_activities_has_expected_keys(self, client):
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        for _, data in activities_data.items():
            assert set(data.keys()) == expected_keys
            assert isinstance(data["participants"], list)


class TestSignupForActivity:
    def test_signup_new_email_adds_to_participants(self, client):
        # Arrange
        activity_name = "Basketball Team"
        email = "new_student@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        activities_data = client.get("/activities").json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_email_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Unicorn Hunting"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404


class TestUnregisterFromActivity:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Swimming Club"
        email = "swimmer@mergington.edu"
        client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        activities_data = client.get("/activities").json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_not_signed_up_returns_400(self, client):
        # Arrange
        activity_name = "Art Studio"
        email = "not_signed_up@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404


class TestSignupAndUnregisterCycle:
    def test_signup_then_unregister_cycle(self, client):
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"

        # Act
        signup_resp = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})
        assert signup_resp.status_code == 200

        # Assert signup
        activities_data = client.get("/activities").json()
        assert email in activities_data[activity_name]["participants"]

        # Act unregister
        unregister_resp = client.post(f"/activities/{quote(activity_name)}/unregister", params={"email": email})
        assert unregister_resp.status_code == 200

        # Assert unregister
        activities_data = client.get("/activities").json()
        assert email not in activities_data[activity_name]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        # Arrange
        activity_name = "Debate Team"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # Act sign up
        for e in emails:
            r = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": e})
            assert r.status_code == 200

        # Assert signed
        activities_data = client.get("/activities").json()
        for e in emails:
            assert e in activities_data[activity_name]["participants"]

        # Act unregister middle
        r = client.post(f"/activities/{quote(activity_name)}/unregister", params={"email": emails[1]})
        assert r.status_code == 200

        # Assert final state
        activities_data = client.get("/activities").json()
        participants = activities_data[activity_name]["participants"]
        assert emails[0] in participants
        assert emails[1] not in participants
        assert emails[2] in participants
