from datetime import datetime, timedelta
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from enum import Enum

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Website(db.Model):
    __tablename__ = "website"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(nullable=False)
    login_url: Mapped[str] = mapped_column(nullable=False)
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

class CustomAccess(db.Model):
    __tablename__ = "custom_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    username_xpath: Mapped[str] = mapped_column(nullable=False)
    password_xpath: Mapped[str] = mapped_column(nullable=False)
    pin_xpath: Mapped[Optional[str]] = mapped_column(nullable=True)
    submit_button_xpath: Mapped[str] = mapped_column(nullable=False)

    website_id: Mapped[int] = mapped_column(ForeignKey("website.id"))


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


class ActionHistory(db.Model):
    __tablename__ = "action_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_started: Mapped[datetime] = mapped_column(nullable=False)
    execution_ended: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    execution_status: Mapped[Optional[ActionStatusCode]] = mapped_column(nullable=False)
    failed_details: Mapped[Optional[ActionFailedDetails]] = mapped_column(nullable=True)

    website_id: Mapped[int] = mapped_column(db.ForeignKey("website.id"), nullable=False)

class ActionInterval(db.Model):
    __tablename__ = "action_interval"

    id: Mapped[int] = mapped_column(primary_key=True)
    interval_start: Mapped[timedelta] = mapped_column(nullable=False)
    interval_end: Mapped[timedelta] = mapped_column(nullable=False)
    interval_hours_min: Mapped[int] = mapped_column(nullable=False)
    interval_hours_max: Mapped[int] = mapped_column(nullable=False)

    website_id: Mapped[int] = mapped_column(ForeignKey("website.id"))

