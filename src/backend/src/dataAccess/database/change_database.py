from datetime import datetime, timezone
from typing import List, Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from dataAccess.database.database import (
    Website,
    User,
    ActionHistory,
    ActionFailedDetails,
    ActionStatusCode,
    Notification,
    get_session,
)
from utils.exceptions import NotFoundException

SECRET_KEY = "your_secret_key"  # Must match main.py
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class DataBase:
    """--------------------------- USER ACCESS ---------------------------"""

    @staticmethod
    def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        with get_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise credentials_exception
            return user

    @staticmethod
    def get_websites(current_user: User) -> List[Website]:
        with get_session() as session:
            user = (
                session.query(User)
                .options(
                    joinedload(User.websites).joinedload(Website.custom_access),
                    joinedload(User.websites).joinedload(Website.action_interval),
                )
                .get(current_user.id)
            )
            return user.websites

    @staticmethod
    def get_website(website_id: int) -> Website:
        with get_session() as session:
            current_user = DataBase.get_current_user()
            query = session.query(Website).filter_by(
                id=website_id, user=current_user.id
            )
            query = query.options(
                joinedload(Website.custom_access), joinedload(Website.action_interval)
            )
            website = query.first()

            if website:
                return website
            raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def add_website(website: Website):
        with get_session() as session:
            current_user = DataBase.get_current_user()
            website.user = current_user.id
            website.next_schedule = datetime.now()
            session.add(website)
            session.commit()

    @staticmethod
    def edit_website(website: Website):
        with get_session() as session:
            existing_website = session.query(Website).filter_by(id=website.id).first()
            if existing_website:
                session.merge(website)
                session.commit()
            else:
                raise NotFoundException(f"Website {website.id} not found")

    @staticmethod
    def delete_website(website_id: int):
        with get_session() as session:
            existing_website = session.query(Website).filter_by(id=website_id).first()
            if existing_website:
                session.delete(existing_website)
                session.commit()
            else:
                raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def trigger_login(website_id: int):
        with get_session() as session:
            current_user = DataBase.get_current_user()
            website = (
                session.query(Website)
                .filter_by(id=website_id, user=current_user.id)
                .first()
            )
            if website:
                website.next_schedule = datetime.now()
                session.commit()
            else:
                raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def get_action_history(website_id: int) -> List[ActionHistory]:
        with get_session() as session:
            current_user = DataBase.get_current_user()
            website = session.get(Website, website_id)
            if website is None or website.user != current_user.id:
                raise NotFoundException(f"Website {website_id} not found")
            return sorted(
                website.action_histories,
                key=lambda ah: ah.execution_started,
                reverse=True,
            )

    @staticmethod
    def add_manual_action_history(website_id: int, action_history: ActionHistory):
        with get_session() as session:
            current_user = DataBase.get_current_user()
            website = session.get(Website, website_id)
            if website is None or website.user != current_user.id:
                raise NotFoundException("Website not found")
            else:
                DataBase.add_action_history(website_id, action_history)

    @staticmethod
    def add_notification(notification: Notification):
        with get_session() as session:
            current_user = DataBase.get_current_user()
            notification.user = current_user.id
            session.add(notification)
            session.commit()

    @staticmethod
    def get_notification(notification_id: int) -> Notification:
        with get_session() as session:
            current_user = DataBase.get_current_user()
            notification = (
                session.query(Notification)
                .filter_by(id=notification_id, user=current_user.id)
                .first()
            )
            if notification:
                return notification
            raise NotFoundException(f"Notification {notification_id} not found")

    @staticmethod
    def edit_notification(notification: Notification):
        with get_session() as session:
            existing_notification = (
                session.query(Notification).filter_by(id=notification.id).first()
            )
            if existing_notification:
                session.merge(notification)
                session.commit()
            else:
                raise NotFoundException(f"Notification {notification.id} not found")

    @staticmethod
    def delete_notification(notification: Notification):
        with get_session() as session:
            existing_notification = (
                session.query(Notification).filter_by(id=notification.id).first()
            )
            if existing_notification:
                session.delete(existing_notification)
                session.commit()
            else:
                raise NotFoundException(f"Notification {notification.id} not found")

    @staticmethod
    def get_notifications() -> List[Notification]:
        with get_session() as session:
            current_user = DataBase.get_current_user()
            notifications = (
                session.query(Notification).filter_by(user=current_user.id).all()
            )
            return notifications

    """--------------------------- INTERNAL ACCESS ---------------------------"""

    @staticmethod
    def get_user(username: str) -> User:
        with get_session() as session:
            return session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_website_by_id(website_id: int) -> Website:
        with get_session() as session:
            website = session.query(Website).filter_by(id=website_id).first()
            if website:
                return website
            raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def get_notifications_all_users() -> List[Notification]:
        with get_session() as session:
            return session.query(Notification).all()

    @staticmethod
    def get_notifications_for_user(action_history: ActionHistory) -> List[Notification]:
        with get_session() as session:
            user_id = (
                session.query(Website).filter_by(id=action_history.website).first().user
            )
            return (
                session.query(Notification)
                .filter_by(user=user_id)
                .filter(
                    Notification._triggers.like(
                        f"%{action_history.execution_status.value}%"
                    )
                )
                .all()
            )

    @staticmethod
    def get_websites_all_users() -> List[Website]:
        with get_session() as session:
            stmt = select(Website).options(
                selectinload(Website.custom_access),
                selectinload(Website.action_interval),
            )
            return session.scalars(stmt).all()

    @staticmethod
    def get_website_all_users(website_id: int) -> Website:
        with get_session() as session:
            website = (
                session.query(Website)
                .options(
                    joinedload(Website.custom_access),
                    joinedload(Website.action_interval),
                )
                .filter_by(id=website_id)
                .first()
            )

            if not website:
                raise NotFoundException(f"Website {website_id} not found")

            return website

    @staticmethod
    def action_history_finish_execution(
        action_history_id: int,
        execution_status: ActionStatusCode,
        failed_details: ActionFailedDetails,
        screenshot_id: str = None,
    ):
        with get_session() as session:
            existing_action_history = session.get(ActionHistory, action_history_id)
            if existing_action_history is None:
                return
            existing_action_history.execution_ended = datetime.now()
            existing_action_history.execution_status = execution_status
            existing_action_history.failed_details = failed_details
            existing_action_history.screenshot_id = screenshot_id
            session.commit()

    @staticmethod
    def unexpected_execution_failure(
        website_id: int, execution_started: datetime
    ) -> List[int]:
        with get_session() as session:
            running_action_histories = (
                session.query(ActionHistory)
                .filter(
                    ActionHistory.execution_status == ActionStatusCode.IN_PROGRESS,
                    ActionHistory.website == website_id,
                )
                .all()
            )
            action_history_ids = []
            for action_history in running_action_histories:
                action_history.execution_status = ActionStatusCode.FAILED
                action_history.execution_ended = datetime.now()
                action_history.failed_details = (
                    ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
                )
                action_history_ids.append(action_history.id)
            if len(running_action_histories) == 0:
                action_history_id = DataBase.add_action_history(
                    website_id,
                    ActionHistory(
                        execution_status=ActionStatusCode.FAILED,
                        execution_started=execution_started,
                        execution_ended=datetime.now(),
                        failed_details=ActionFailedDetails.UNKNOWN_EXECUTION_ERROR,
                    ),
                )
                action_history_ids.append(action_history_id)
            session.commit()
            return action_history_ids

    @staticmethod
    def add_action_history(website_id: int, action_history: ActionHistory) -> int:
        with get_session() as session:
            website = session.get(Website, website_id)
            website.action_histories.append(action_history)
            if website.paused:
                website.next_schedule = None  # In order to prevent race conditions
            else:
                website.next_schedule = (
                    website.action_interval.get_random_action_datetime()
                )
            session.commit()
            return action_history.id
