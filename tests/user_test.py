import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from src.classes.auth import IncorrectPassword, Auth, UserNotFound, UserDisabled

client = TestClient(app)


@pytest.fixture
def mock_authenticated_user():
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.verify_password.return_value = True
    mock_user.disabled = False

    mock_session = MagicMock()
    mock_session.__enter__.return_value.exec.return_value.first.return_value = mock_user

    with patch("src.classes.auth.Session", return_value=mock_session), patch(
        "src.classes.auth.jwt.encode", return_value="fake_token"
    ):
        yield


@pytest.fixture
def mock_user_not_found():
    mock_session = MagicMock()
    mock_session.__enter__.return_value.exec.return_value.first.return_value = None

    with patch("src.classes.auth.Session", return_value=mock_session):
        yield


@pytest.fixture
def mock_user_incorrect_password():
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.verify_password.return_value = False
    mock_user.disabled = False

    mock_session = MagicMock()
    mock_session.__enter__.return_value.exec.return_value.first.return_value = mock_user

    with patch("src.classes.auth.Session", return_value=mock_session):
        yield


@pytest.fixture
def mock_user_disabled():
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.verify_password.return_value = True
    mock_user.disabled = True

    mock_session = MagicMock()
    mock_session.__enter__.return_value.exec.return_value.first.return_value = mock_user

    with patch("src.classes.auth.Session", return_value=mock_session):
        yield


def test_login_success(mock_authenticated_user):
    email = "test@example.com"
    password = "test_password"
    response = Auth.login(email, password)

    assert "access_token" in response
    assert response["access_token"] == "fake_token"


def test_login_user_not_found(mock_user_not_found):
    email = "nonexistent@example.com"
    password = "test_password"
    with pytest.raises(UserNotFound):
        Auth.login(email, password)


def test_login_incorrect_password(mock_user_incorrect_password):
    email = "test@example.com"
    password = "wrong_password"
    with pytest.raises(IncorrectPassword):
        Auth.login(email, password)


def test_login_user_disabled(mock_user_disabled):
    email = "test@example.com"
    password = "test_password"
    with pytest.raises(UserDisabled):
        Auth.login(email, password)
