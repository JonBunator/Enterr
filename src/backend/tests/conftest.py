from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dataAccess.database.database import (
    Base,
    User,
    Website,
    ActionInterval,
    db_session,
)
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints


@pytest.fixture
def engine():
    """In-memory SQLite engine shared across sessions/threads of a single test"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine, mocker):
    """Redirects every get_db()/get_db_session() call to the in-memory database"""
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    mocker.patch("dataAccess.database.database.SessionLocal", factory)
    return factory


@pytest.fixture
def session(session_factory):
    """Session that is also registered as the request scoped db_session"""
    session = session_factory()
    token = db_session.set(session)
    yield session
    db_session.reset(token)
    session.close()


def _create_user(session, username: str, password: str) -> User:
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def user(session):
    return _create_user(session, "testuser", "testpass123")


@pytest.fixture
def other_user(session):
    return _create_user(session, "otheruser", "otherpass123")


@pytest.fixture
def make_website(session, user):
    """Factory that persists a website (owned by `user` unless `owner` is given)"""

    def _make_website(owner: User = None, action_interval: ActionInterval = None, **overrides) -> Website:
        values = dict(
            url="https://example.com/login",
            success_url="https://example.com/home",
            name="Example",
            username="user123",
            password="password123",
            added_at=datetime(2020, 1, 1, 2, 43),
            take_screenshot=False,
            paused=False,
            user=(owner or user).id,
        )
        values.update(overrides)
        website = Website(**values)
        website.action_interval = action_interval or ActionInterval(
            date_minutes_start=1440,
            date_minutes_end=None,
            allowed_time_minutes_start=None,
            allowed_time_minutes_end=None,
        )
        session.add(website)
        session.commit()
        session.refresh(website)
        return website

    return _make_website


@pytest.fixture
def webhooks(mocker):
    return mocker.Mock(spec=WebhookEndpoints)
