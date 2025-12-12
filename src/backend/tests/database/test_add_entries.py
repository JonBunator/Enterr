from datetime import datetime, timedelta
from dataAccess.database.database import (
    Website,
    User,
    CustomAccess,
    ActionHistory,
    ActionStatusCode,
    ActionFailedDetails,
    ActionInterval,
    Base,
    engine,
    SessionLocal,
    get_session,
)
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_engine():
    """Create a test engine with in-memory SQLite database"""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture
def test_session(test_engine):
    """Create a test session"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(test_session):
    """Create a test user"""
    user = User(username="testuser", password="testpass123")
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


def create_website(dt: datetime, user_id: int) -> Website:
    return Website(
        url="https://example.com",
        success_url="https://example.com/login",
        name="Example",
        username="user123",
        password="password123",
        added_at=dt,
        expiration_interval=timedelta(days=1),
        next_schedule=dt,
        take_screenshot=True,
        paused=False,
        user=user_id,
    )


def test_website_entry_creation(test_session, test_user):
    """Tests the creation of a website entry."""
    dt = datetime(2020, 1, 1, 2, 43)
    new_website = create_website(dt, test_user.id)

    test_session.add(new_website)
    test_session.commit()

    website_in_db = test_session.query(Website).first()
    assert website_in_db is not None
    assert website_in_db.url == "https://example.com"
    assert website_in_db.success_url == "https://example.com/login"
    assert website_in_db.name == "Example"
    assert website_in_db.username == "user123"
    assert website_in_db.password == "password123"
    assert website_in_db.added_at == dt
    assert website_in_db.expiration_interval == timedelta(days=1)
    assert website_in_db.take_screenshot is True
    assert website_in_db.paused is False
    assert website_in_db.next_schedule == dt
    assert website_in_db.user == test_user.id


def test_website_entry_creation_null_values(test_session, test_user):
    new_website = Website(
        url="https://example.com",
        success_url="https://example.com/login",
        name="Example",
        username="user123",
        password="password123",
        added_at=datetime.now(),
        take_screenshot=False,
        paused=False,
        user=test_user.id,
    )
    test_session.add(new_website)
    test_session.commit()

    website_in_db = test_session.query(Website).first()

    assert website_in_db is not None
    assert website_in_db.expiration_interval is None
    assert website_in_db.next_schedule is None


def test_website_with_action_history(test_session, test_user):
    """Test that ActionHistory objects are correctly added to a Website."""
    website = create_website(datetime.now(), test_user.id)

    dt = datetime(2020, 1, 1, 2, 43)

    action_history_1 = ActionHistory(
        execution_started=dt,
        execution_ended=dt + timedelta(minutes=1),
        execution_status=ActionStatusCode.SUCCESS,
        failed_details=None,
    )
    action_history_2 = ActionHistory(
        execution_started=dt,
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.USERNAME_FIELD_NOT_FOUND,
    )

    website.action_histories.extend([action_history_1, action_history_2])
    test_session.add(website)
    test_session.commit()

    retrieved_website = test_session.query(Website).filter_by(name="Example").one()

    assert retrieved_website is not None
    assert len(retrieved_website.action_histories) == 2

    history1 = retrieved_website.action_histories[0]
    assert history1.execution_started == dt
    assert history1.execution_ended == dt + timedelta(minutes=1)
    assert history1.execution_status == ActionStatusCode.SUCCESS
    assert history1.failed_details is None

    history2 = retrieved_website.action_histories[1]
    assert history2.execution_started == dt
    assert history2.execution_ended is None
    assert history2.execution_status == ActionStatusCode.FAILED
    assert history2.failed_details == ActionFailedDetails.USERNAME_FIELD_NOT_FOUND


def test_website_with_action_intervals(test_session, test_user):
    """Test that ActionInterval objects are correctly added to a Website."""
    website = create_website(datetime.now(), test_user.id)
    interval = ActionInterval(
        date_minutes_start=1440,
        date_minutes_end=2880,
        allowed_time_minutes_start=60,
        allowed_time_minutes_end=80,
    )

    website.action_interval = interval
    test_session.add(website)
    test_session.commit()

    retrieved_website = test_session.query(Website).filter_by(name="Example").one()

    assert retrieved_website is not None

    interval = retrieved_website.action_interval
    assert interval.date_minutes_start == 1440
    assert interval.date_minutes_end == 2880
    assert interval.allowed_time_minutes_start == 60
    assert interval.allowed_time_minutes_end == 80


def test_website_with_action_intervals_none_values(test_session, test_user):
    """Test that ActionInterval objects are correctly added to a Website with none values."""
    website = create_website(datetime.now(), test_user.id)
    interval = ActionInterval(
        date_minutes_start=5,
        date_minutes_end=None,
        allowed_time_minutes_start=None,
        allowed_time_minutes_end=None,
    )

    website.action_interval = interval
    test_session.add(website)
    test_session.commit()

    retrieved_website = test_session.query(Website).filter_by(name="Example").one()

    assert retrieved_website is not None

    interval = retrieved_website.action_interval
    assert interval.date_minutes_start == 5
    assert interval.date_minutes_end_not_none == 5
    assert interval.allowed_time_minutes_start_not_none == 0
    assert interval.allowed_time_minutes_end_not_none == 1440
