from datetime import datetime, timedelta
from random import randint
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import ForeignKey
from enum import Enum

_db = SQLAlchemy()

def init_db(app):
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        _db.init_app(app)
        _db.create_all()

class Website(_db.Model):
    __tablename__ = "website"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(nullable=False)
    success_url: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    pin: Mapped[Optional[str]] = mapped_column(nullable=True)
    added_at: Mapped[datetime] = mapped_column(nullable=False)
    expiration_interval: Mapped[Optional[timedelta]] = mapped_column(nullable=True)
    next_schedule: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationship to CustomAccess
    custom_access: Mapped[Optional["CustomAccess"]] = relationship()

    # Relationship to ActionHistory
    action_histories: Mapped[List["ActionHistory"]] = relationship()

    # Relationship to ActionInterval
    action_interval: Mapped["ActionInterval"] = relationship()

class CustomAccess(_db.Model):
    __tablename__ = "custom_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    username_xpath: Mapped[str] = mapped_column(nullable=False)
    password_xpath: Mapped[str] = mapped_column(nullable=False)
    pin_xpath: Mapped[Optional[str]] = mapped_column(nullable=True)
    submit_button_xpath: Mapped[str] = mapped_column(nullable=False)

    website: Mapped[int] = mapped_column(ForeignKey("website.id"))


class ActionStatusCode(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ActionFailedDetails(Enum):
    AUTOMATIC_FORM_DETECTION_FAILED = "AUTOMATIC_FORM_DETECTION_FAILED"
    USERNAME_FIELD_NOT_FOUND = "USERNAME_FIELD_NOT_FOUND"
    PASSWORD_FIELD_NOT_FOUND = "PASSWORD_FIELD_NOT_FOUND"
    PIN_FIELD_NOT_FOUND = "PIN_FIELD_NOT_FOUND"
    SUBMIT_BUTTON_NOT_FOUND = "SUBMIT_BUTTON_NOT_FOUND"

class ActionHistory(_db.Model):
    __tablename__ = "action_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_started: Mapped[datetime] = mapped_column(nullable=False)
    execution_ended: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    execution_status: Mapped[ActionStatusCode] = mapped_column(nullable=False)
    failed_details: Mapped[Optional[ActionFailedDetails]] = mapped_column(nullable=True)

    website: Mapped[int] = mapped_column(_db.ForeignKey("website.id"), nullable=False)

class ActionInterval(_db.Model):
    __tablename__ = "action_interval"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_minutes_start: Mapped[int] = mapped_column(nullable=False)
    date_minutes_end: Mapped[int] = mapped_column(nullable=False)
    allowed_time_minutes_start: Mapped[int] = mapped_column(nullable=False)
    allowed_time_minutes_end: Mapped[int] = mapped_column(nullable=False)

    website_id: Mapped[int] = mapped_column(ForeignKey("website.id"))

    def __init__(self, date_minutes_start, date_minutes_end, allowed_time_minutes_start, allowed_time_minutes_end):
        self.date_minutes_start = date_minutes_start
        self.date_minutes_end = date_minutes_end
        self.allowed_time_minutes_start = allowed_time_minutes_start
        self.allowed_time_minutes_end = allowed_time_minutes_end

        self.validate_date_range()

    def validate_date_range(self):
        """
        Custom validation to ensure that date_minutes_start and date_minutes_end are
        valid according to allowed_time_minutes_start and allowed_time_minutes_end.
        """
        if self.allowed_time_minutes_start == 0 and self.allowed_time_minutes_end == 1440:
            # If allowed_time_minutes_start = 0 and allowed_time_minutes_end = 1440, allow any value
            return
        else:
            # Otherwise, check if the value is a multiple of 1440 (i.e., a full day in minutes)
            if self.date_minutes_start % 1440 != 0:
                raise ValueError(f"date_minutes_start must be a multiple of 1440 minutes.")
            if self.date_minutes_end % 1440 != 0:
                raise ValueError(f"date_minutes_end must be a multiple of 1440 minutes.")


    def get_random_action_datetime(self) -> datetime:
        """
        Gets random datetime between interval_minutes_start to interval_minutes_end date offset
        and interval_minutes_min to interval_minutes_max time offset.
        @return: Random datetime.
        """

        random_date_delta = randint(self.date_minutes_start, self.date_minutes_end)
        random_date = datetime.now() + timedelta(minutes=random_date_delta)
        if self.date_minutes_start % 1440 == 0 and self.date_minutes_end % 1440 == 0:
            random_time = randint(self.allowed_time_minutes_start, self.allowed_time_minutes_end)
            random_datetime = datetime.combine(random_date, datetime.min.time()) + timedelta(minutes=random_time)
        else:
            random_datetime = random_date
        return random_datetime



