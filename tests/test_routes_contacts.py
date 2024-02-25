from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import pytest

from src.database.model import User, Contact
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch: pytest.MonkeyPatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def contact():
    return {
        "first_name": "unknown",
        "last_name": "unknown",
        "email": "unknown@aa.com",
        "phone": "??-???-???-???",
        "born_date": str(datetime(year=1999, month=12, day=12).date()),
        "additional": "none",
    }


@pytest.fixture(scope="module")
def contact_updated(contact):
    contact["additional"] = "he is stupid"
    return contact


def test_add_new_contact(client, token, contact):

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json=contact,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()

        assert "id" in data
        for key, value in contact.items():
            assert data[key] == value


def get_all_contats(client, token, list_len):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == list_len


def test_get_all_contacts(client, token):
    get_all_contats(client, token, list_len=1)


def test_get_contacts_by_field_example(client, token):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/api/contacts/byfield?field=id&value=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 1


def test_get_contacts_by_field_example_not_found(client, token):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/api/contacts/byfield?field=id&value=2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


def test_get_contact(client, token, contact):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        assert response.status_code == 200
        for key, value in contact.items():
            assert data[key] == value


def test_get_contacts_with_birthday_upcoming(client, token):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/api/contacts/birthday",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        assert response.status_code == 200
        assert isinstance(data, list)


def test_update_contact(client, token, contact_updated):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json=contact_updated,
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()
        for key, value in contact_updated.items():
            assert data[key] == value


def test_update_contact_not_found(client, token, contact_updated):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.put(
            "/api/contacts/2",
            json=contact_updated,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


def test_delete_contact_not_found(client, token):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


def test_delete_contact(client, token, contact_updated):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()
        for key, value in contact_updated.items():
            assert data[key] == value
        get_all_contats(client, token, list_len=0)
