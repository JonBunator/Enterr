from hashlib import pbkdf2_hmac
import os


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
