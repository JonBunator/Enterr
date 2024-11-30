from datetime import datetime, timedelta
from flask import Flask
from database.database import Website, db, CustomAccess, ActionHistory, ActionStatusCode, ActionFailedDetails, \
    ActionInterval

import pytest

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.drop_all()

def create_website(dt: datetime) -> Website:
    return Website(
        url="https://example.com",
        login_url="https://example.com/login",
        name="Example",
        username="user123",
        password="password123",
        pin="1234",
        added_at=dt,
        expiration_interval=timedelta(days=1),
        next_schedule=dt,
    )

def test_website_entry_creation(app):
    """Tests the creation of a website entry."""
    with app.app_context():
        now = datetime.now()
        new_website = create_website(now)

        db.session.add(new_website)
        db.session.commit()

        website_in_db = Website.query.first()
        assert website_in_db is not None
        assert website_in_db.url == "https://example.com"
        assert website_in_db.login_url == "https://example.com/login"
        assert website_in_db.name == "Example"
        assert website_in_db.username == "user123"
        assert website_in_db.password == "password123"
        assert website_in_db.pin == "1234"
        assert website_in_db.added_at == now
        assert website_in_db.expiration_interval == timedelta(days=1)
        assert website_in_db.next_schedule == now

def test_website_entry_creation_null_values(app):
    """Tests website creation with no pin."""
    with app.app_context():
        new_website = Website(
            url="https://example.com",
            login_url="https://example.com/login",
            name="Example",
            username="user123",
            password="password123",
            added_at=datetime.now()
        )
        db.session.add(new_website)
        db.session.commit()

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
        db.session.add(website)
        db.session.commit()

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

        now = datetime.now()

        action_history_1 = ActionHistory(
            execution_started=now,
            execution_ended=now + timedelta(minutes=1),
            execution_status=ActionStatusCode.SUCCESS,
            failed_details=None
        )
        action_history_2 = ActionHistory(
            execution_started=datetime.now(),
            execution_status=ActionStatusCode.FAILED,
            failed_details=ActionFailedDetails.USERNAME_FIELD_NOT_FOUND
        )

        website.action_histories.extend([action_history_1, action_history_2])
        db.session.add(website)
        db.session.commit()

        retrieved_website = Website.query.filter_by(name="Example").one()

        assert retrieved_website is not None
        assert len(retrieved_website.action_histories) == 2

        history1 = retrieved_website.action_histories[0]
        assert history1.execution_started == now
        assert history1.execution_ended == now + timedelta(minutes=1)
        assert history1.execution_status == ActionStatusCode.SUCCESS
        assert history1.failed_details is None

        history2 = retrieved_website.action_histories[1]
        assert history2.execution_started == now
        assert history2.execution_ended is None
        assert history2.execution_status == ActionStatusCode.FAILED
        assert history2.failed_details == ActionFailedDetails.USERNAME_FIELD_NOT_FOUND

def test_website_with_action_intervals(app):
    """Test that ActionInterval objects are correctly added to a Website."""
    with app.app_context():
        website = create_website(datetime.now())

        interval = ActionInterval(
            interval_start=timedelta(hours=8),
            interval_end=timedelta(hours=12),
            interval_hours_min=2,
            interval_hours_max=4,
        )

        website.action_interval = interval
        db.session.add(website)
        db.session.commit()

        retrieved_website = Website.query.filter_by(name="Example").one()

        assert retrieved_website is not None

        interval = retrieved_website.action_interval
        assert interval.interval_start == timedelta(hours=8)
        assert interval.interval_end == timedelta(hours=12)
        assert interval.interval_hours_min == 2
        assert interval.interval_hours_max == 4
