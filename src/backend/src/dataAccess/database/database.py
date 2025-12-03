import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from random import randint
from typing import List, Optional
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    declarative_base,
    sessionmaker,
)
from sqlalchemy import ForeignKey
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from utils.security import get_database_key, get_database_pepper
from alembic.config import Config
from alembic import command
import sys

try:
    import sqlcipher3
except ImportError:
    sqlcipher3 = None

Base = declarative_base()

dev_mode = os.getenv("RUN_MODE") != "production"


def get_database_uri() -> str:
    """Get the database URI based on the current environment."""
    if dev_mode:
        return "sqlite:///database.db"
    else:
        db_key = get_database_key()
        return f"sqlite+pysqlcipher://:{db_key}@//config/database.db"


database_uri = get_database_uri()

if dev_mode:
    engine = create_engine(database_uri)
else:
    # Encrypted database in production
    if sqlcipher3 is None:
        raise ImportError("sqlcipher3 is required for encrypted database in production")
    engine = create_engine(database_uri, module=sqlcipher3)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database with Alembic migrations"""
    # In dev mode, just create all tables without migrations
    if dev_mode:
        Base.metadata.create_all(engine)
        return

    # Production mode: use Alembic migrations
    alembic_cfg = Config("src/alembic.ini", stdout=sys.stdout)
    alembic_cfg.set_main_option("script_location", "src/migrations")

    # Check if database file exists
    if not os.path.exists("/config/database.db"):
        Base.metadata.create_all(engine)
        command.stamp(alembic_cfg, "head", sql=False)
        return

    inspector = inspect(engine)
    if "alembic_version" not in inspector.get_table_names():
        command.stamp(alembic_cfg, "8e6efc857763", sql=False)

    command.upgrade(alembic_cfg, "head", sql=False)


@contextmanager
def get_session():
    with SessionLocal() as session:
        yield session


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
    BUTTON_NOT_FOUND = "BUTTON_NOT_FOUND"
    TEXT_FIELD_NOT_FOUND = "TEXT_FIELD_NOT_FOUND"
    SUCCESS_URL_DID_NOT_MATCH = "SUCCESS_URL_DID_NOT_MATCH"
    UNKNOWN_EXECUTION_ERROR = "UNKNOWN_EXECUTION_ERROR"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    # Relationship to Notifications
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", cascade="all, delete-orphan", backref="parent_user"
    )

    # Relationship to Website
    websites: Mapped[List["Website"]] = relationship(
        "Website", cascade="all, delete-orphan", backref="parent_user"
    )

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        pepper = get_database_pepper()
        self.password_hash = generate_password_hash(password + pepper)

    def check_password(self, password):
        pepper = get_database_pepper()
        return check_password_hash(self.password_hash, password + pepper)


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    apprise_token: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    _triggers: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[int] = mapped_column(ForeignKey("user.id"))

    @property
    def triggers(self) -> List[ActionStatusCode]:
        return [ActionStatusCode(val) for val in self._triggers.split(";") if val]

    @triggers.setter
    def triggers(self, value: List[ActionStatusCode]):
        self._triggers = ";".join(v.value for v in value)


class Website(Base):
    __tablename__ = "website"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(nullable=False)
    success_url: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    pin: Mapped[Optional[str]] = mapped_column(nullable=True)
    added_at: Mapped[datetime] = mapped_column(nullable=False)
    take_screenshot: Mapped[bool] = mapped_column(nullable=False)
    paused: Mapped[bool] = mapped_column(nullable=False)
    expiration_interval: Mapped[Optional[timedelta]] = mapped_column(nullable=True)
    next_schedule: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    user: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Relationship to CustomAccess
    custom_access: Mapped[Optional["CustomAccess"]] = relationship(
        "CustomAccess",
        cascade="all, delete-orphan",
        backref="parent_website",
        uselist=False,
    )

    # Relationship to ActionHistory
    action_histories: Mapped[List["ActionHistory"]] = relationship(
        "ActionHistory", cascade="all, delete-orphan", backref="parent_website"
    )

    # Relationship to ActionInterval
    action_interval: Mapped["ActionInterval"] = relationship(
        "ActionInterval",
        cascade="all, delete-orphan",
        backref="parent_website",
        uselist=False,
    )


class CustomAccess(Base):
    __tablename__ = "custom_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    username_xpath: Mapped[str] = mapped_column(nullable=True)
    password_xpath: Mapped[str] = mapped_column(nullable=True)
    pin_xpath: Mapped[Optional[str]] = mapped_column(nullable=True)
    submit_button_xpath: Mapped[str] = mapped_column(nullable=True)

    website: Mapped[int] = mapped_column(ForeignKey("website.id"))


class ActionHistory(Base):
    __tablename__ = "action_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_started: Mapped[datetime] = mapped_column(nullable=False)
    execution_ended: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    execution_status: Mapped[ActionStatusCode] = mapped_column(nullable=False)
    failed_details: Mapped[Optional[ActionFailedDetails]] = mapped_column(nullable=True)
    custom_failed_details_message: Mapped[Optional[str]] = mapped_column(nullable=True)
    screenshot_id: Mapped[Optional[str]] = mapped_column(nullable=True)

    website: Mapped[int] = mapped_column(ForeignKey("website.id"), nullable=False)


class ActionInterval(Base):
    __tablename__ = "action_interval"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_minutes_start: Mapped[int] = mapped_column(nullable=False)
    date_minutes_end: Mapped[int] = mapped_column(nullable=True)
    allowed_time_minutes_start: Mapped[int] = mapped_column(nullable=True)
    allowed_time_minutes_end: Mapped[int] = mapped_column(nullable=True)

    website_id: Mapped[int] = mapped_column(ForeignKey("website.id"))

    def __init__(
        self,
        date_minutes_start,
        date_minutes_end,
        allowed_time_minutes_start,
        allowed_time_minutes_end,
    ):
        self.date_minutes_start = date_minutes_start
        self.date_minutes_end = date_minutes_end
        self.allowed_time_minutes_start = allowed_time_minutes_start
        self.allowed_time_minutes_end = allowed_time_minutes_end

        self._validate_date_range()

    @hybrid_property
    def date_minutes_end_not_none(self):
        return (
            self.date_minutes_end if self.date_minutes_end else self.date_minutes_start
        )

    @hybrid_property
    def allowed_time_minutes_start_not_none(self):
        return self.allowed_time_minutes_start if self.allowed_time_minutes_start else 0

    @hybrid_property
    def allowed_time_minutes_end_not_none(self):
        return self.allowed_time_minutes_end if self.allowed_time_minutes_end else 1440

    def _validate_date_range(self):
        """
        Custom validation to ensure that date_minutes_start and date_minutes_end are
        valid according to allowed_time_minutes_start and allowed_time_minutes_end.
        """
        if self.date_minutes_start > self.date_minutes_end_not_none:
            raise ValueError(
                "date_minutes_end must be greater than or equal to date_minutes_start"
            )
        if (
            self.allowed_time_minutes_start_not_none
            > self.allowed_time_minutes_end_not_none
        ):
            raise ValueError(
                "allowed_time_minutes_end must be greater than or equal to allowed_time_minutes_start"
            )

        if (
            self.allowed_time_minutes_start_not_none == 0
            and self.allowed_time_minutes_end_not_none == 1440
        ):
            # allow any value
            return
        else:
            # Otherwise, check if the value is a multiple of 1440 (i.e., a full day in minutes)
            if self.date_minutes_start % 1440 != 0:
                raise ValueError(
                    f"date_minutes_start must be a multiple of 1440 minutes."
                )
            if self.date_minutes_end_not_none % 1440 != 0:
                raise ValueError(
                    f"date_minutes_end must be a multiple of 1440 minutes."
                )

    @hybrid_method
    def get_random_action_datetime(self) -> datetime:
        """
        Gets random datetime between interval_minutes_start to interval_minutes_end date offset
        and interval_minutes_min to interval_minutes_max time offset.
        @return: Random datetime.
        """

        random_date_delta = randint(
            self.date_minutes_start, self.date_minutes_end_not_none
        )
        random_date = datetime.now() + timedelta(minutes=random_date_delta)
        if (
            self.date_minutes_start % 1440 == 0
            and self.date_minutes_end_not_none % 1440 == 0
        ):
            random_time = randint(
                self.allowed_time_minutes_start_not_none,
                self.allowed_time_minutes_end_not_none,
            )
            random_datetime = datetime.combine(
                random_date, datetime.min.time()
            ) + timedelta(minutes=random_time)
        else:
            random_datetime = random_date
        return random_datetime
