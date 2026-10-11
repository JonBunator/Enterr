from datetime import datetime, timedelta, timezone

from jose import jwt

from dataAccess.database.database import User
from utils.security import (
    JWT_ALGORITHM,
    create_access_token,
    decode_token,
    get_jwt_secret,
)


def test_access_token_round_trip():
    token = create_access_token("alice")
    assert decode_token(token) == "alice"


def test_decode_token_with_wrong_secret_returns_none():
    token = jwt.encode({"sub": "alice"}, "wrong-secret", algorithm=JWT_ALGORITHM)
    assert decode_token(token) is None


def test_decode_garbage_token_returns_none():
    assert decode_token("not-a-token") is None


def test_decode_expired_token_returns_none():
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "alice", "exp": expired}, get_jwt_secret(), algorithm=JWT_ALGORITHM
    )
    assert decode_token(token) is None


def test_user_password_check():
    user = User(username="alice", password="secret")
    assert user.password_hash != "secret"
    assert user.check_password("secret") is True
    assert user.check_password("wrong") is False


def test_user_set_password_replaces_old_password():
    user = User(username="alice", password="secret")
    user.set_password("new-secret")
    assert user.check_password("new-secret") is True
    assert user.check_password("secret") is False
