from datetime import datetime, timedelta, timezone
from flask import Flask

from dataAccess.database.database import Website, _db, CustomAccess, ActionHistory, ActionStatusCode, ActionFailedDetails, \
    ActionInterval

import pytest

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        _db.init_app(app)
        _db.create_all()
        yield app
        _db.drop_all()

def create_website(dt: datetime) -> Website:
    return Website(
        url="https://example.com",
        success_url="https://example.com/login",
        name="Example",
        username="user123",
        password="password123",
        pin="1234",
        added_at=dt,
        expiration_interval=timedelta(days=1),
        next_schedule=dt,
        take_screenshot=True,
        paused=False,
        user=1,
    )

def test_website_entry_creation(app):
    """Tests the creation of a website entry."""
    with app.app_context():
        dt = datetime(2020, 1, 1, 2, 43)
        new_website = create_website(dt)

        _db.session.add(new_website)
        _db.session.commit()

        website_in_db = Website.query.first()
        assert website_in_db is not None
        assert website_in_db.url == "https://example.com"
        assert website_in_db.success_url == "https://example.com/login"
        assert website_in_db.name == "Example"
        assert website_in_db.username == "user123"
        assert website_in_db.password == "password123"
        assert website_in_db.pin == "1234"
        assert website_in_db.added_at == dt
        assert website_in_db.expiration_interval == timedelta(days=1)
        assert website_in_db.take_screenshot is True
        assert website_in_db.paused is False
        assert website_in_db.next_schedule == dt
        assert website_in_db.user == 1

def test_website_entry_creation_null_values(app):
    """Tests website creation with no pin."""
    with app.app_context():
        new_website = Website(
            url="https://example.com",
            success_url="https://example.com/login",
            name="Example",
            username="user123",
            password="password123",
            added_at=datetime.now(),
            take_screenshot=False,
            paused=False,
            user=1,
        )
        _db.session.add(new_website)
        _db.session.commit()

        website_in_db = Website.query.first()

        assert website_in_db is not None
        assert website_in_db.pin is None
        assert website_in_db.expiration_interval is None
        assert website_in_db.next_schedule is None

def test_website_with_custom_accesses(app):
    """Test that CustomAccess objects are correctly added to a Website."""
    with app.app_context():
        website = create_website(datetime.now())

        custom_access = CustomAccess(
            username_xpath="//input[@name='username']",
            password_xpath="//input[@name='password']",
            submit_button_xpath="//button[@type='submit']"
        )

        website.custom_access = custom_access
        _db.session.add(website)
        _db.session.commit()

        retrieved_website = Website.query.one()

        assert retrieved_website is not None

        access = retrieved_website.custom_access
        assert access.username_xpath == "//input[@name='username']"
        assert access.password_xpath == "//input[@name='password']"
        assert access.submit_button_xpath == "//button[@type='submit']"

def test_website_with_action_history(app):
    """Test that ActionHistory objects are correctly added to a Website."""
    with app.app_context():
        website = create_website(datetime.now())

        dt = datetime(2020, 1, 1, 2, 43)

        action_history_1 = ActionHistory(
            execution_started=dt,
            execution_ended=dt + timedelta(minutes=1),
            execution_status=ActionStatusCode.SUCCESS,
            failed_details=None
        )
        action_history_2 = ActionHistory(
            execution_started=dt,
            execution_status=ActionStatusCode.FAILED,
            failed_details=ActionFailedDetails.USERNAME_FIELD_NOT_FOUND
        )

        website.action_histories.extend([action_history_1, action_history_2])
        _db.session.add(website)
        _db.session.commit()

        retrieved_website = Website.query.filter_by(name="Example").one()

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

def test_website_with_action_intervals(app):
    """Test that ActionInterval objects are correctly added to a Website."""
    with app.app_context():
        website = create_website(datetime.now())
        interval = ActionInterval(
            date_minutes_start=1440,
            date_minutes_end=2880,
            allowed_time_minutes_start=60,
            allowed_time_minutes_end=80,
        )

        website.action_interval = interval
        _db.session.add(website)
        _db.session.commit()

        retrieved_website = Website.query.filter_by(name="Example").one()

        assert retrieved_website is not None

        interval = retrieved_website.action_interval
        assert interval.date_minutes_start == 1440
        assert interval.date_minutes_end == 2880
        assert interval.allowed_time_minutes_start == 60
        assert interval.allowed_time_minutes_end == 80

def test_website_with_action_intervals_none_values(app):
    """Test that ActionInterval objects are correctly added to a Website with none values."""
    with app.app_context():
        website = create_website(datetime.now())
        interval = ActionInterval(
            date_minutes_start=5,
            date_minutes_end=None,
            allowed_time_minutes_start=None,
            allowed_time_minutes_end=None,
        )

        website.action_interval = interval
        _db.session.add(website)
        _db.session.commit()

        retrieved_website = Website.query.filter_by(name="Example").one()

        assert retrieved_website is not None

        interval = retrieved_website.action_interval
        assert interval.date_minutes_start == 5
        assert interval.date_minutes_end_not_none == 5
        assert interval.allowed_time_minutes_start_not_none == 0
        assert interval.allowed_time_minutes_end_not_none == 1440
