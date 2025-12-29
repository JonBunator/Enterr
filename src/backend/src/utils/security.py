from datetime import datetime, timedelta
from hashlib import pbkdf2_hmac
import os
from jose import jwt, JWTError


def _get_secret_key(public_salt: str):
    dev_mode = os.getenv("RUN_MODE") != "production"
    if dev_mode:
        key = "DEBUG_SECRET_KEY"
    else:
        key = os.environ["SECRET_KEY"]
    iterations = 100_000
    return pbkdf2_hmac('sha256', key.encode(), public_salt.encode() * 2, iterations).hex()


def get_database_key():
    return _get_secret_key("SRC4UE2V9NR5M3Z9")


def get_database_pepper():
    return _get_secret_key("9DC3PNZQPMZXNL4T")


def get_jwt_secret():
    return _get_secret_key("WBVCLH2EL7UZECXR")


JWT_ALGORITHM = "HS256"


def create_access_token(username: str):
    to_encode = {"sub": username}
    expire = datetime.now() + timedelta(minutes=24 * 60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None