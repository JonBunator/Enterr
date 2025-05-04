from datetime import datetime, timezone
from typing import List

import flask_login

from dataAccess.database.database import (
    Website,
    User,
    _db as db,
    ActionHistory,
    ActionFailedDetails,
    ActionStatusCode, Notification,
)


class DataBase:
    """--------------------------- USER ACCESS ---------------------------"""

    @staticmethod
    def get_current_user() -> User:
        return flask_login.current_user

    @staticmethod
    def get_websites() -> List[Website]:
        user = DataBase.get_current_user()
        return user.websites

    @staticmethod
    def get_website(website_id: int) -> Website:
        current_user = DataBase.get_current_user()
        website = (
            db.session.query(Website)
            .filter_by(id=website_id, user=current_user.id)
            .first()
        )
        if website:
            return website
        raise Exception(f"Website {website_id} not found")

    @staticmethod
    def add_website(website: Website):
        current_user = DataBase.get_current_user()
        website.user = current_user.id
        website.next_schedule = datetime.now(timezone.utc)
        db.session.add(website)
        db.session.commit()

    @staticmethod
    def edit_website(website: Website):
        website = DataBase.get_website(website.id)
        if website:
            db.session.merge(website)
            db.session.commit()
        else:
            raise Exception(f"Website {website.id} not found")

    @staticmethod
    def delete_website(website: Website):
        website = DataBase.get_website(website.id)
        if website:
            db.session.delete(website)
            db.session.commit()
        else:
            raise Exception(f"Website {website.id} not found")

    @staticmethod
    def trigger_login(website_id: int):
        current_user = DataBase.get_current_user()
        website = (
            db.session.query(Website)
            .filter_by(id=website_id, user=current_user.id)
            .first()
        )
        if website:
            website.next_schedule = datetime.now(timezone.utc)
            db.session.commit()
        else:
            raise Exception(f"Website {website.id} not found")

    @staticmethod
    def get_action_history(website_id: int) -> List[ActionHistory]:
        current_user = DataBase.get_current_user()
        website = db.session.get(Website, website_id)
        if website is None or website.user != current_user.id:
            raise Exception(f"Website {website_id} not found")
        return sorted(
            website.action_histories,
            key=lambda ah: ah.execution_started,
            reverse=True,
        )

    @staticmethod
    def add_manual_action_history(website_id: int, action_history: ActionHistory):
        current_user = DataBase.get_current_user()
        website = db.session.get(Website, website_id)
        if website is None or website.user != current_user.id:
            raise Exception("Website not found")
        else:
            DataBase.add_action_history(website_id, action_history)

    @staticmethod
    def add_notification(notification: Notification):
        current_user = DataBase.get_current_user()
        notification.user = current_user.id
        db.session.add(notification)
        db.session.commit()

    @staticmethod
    def get_notification(notification_id: int) -> Notification:
        current_user = DataBase.get_current_user()
        notification = (
            db.session.query(Notification)
            .filter_by(id=notification_id, user=current_user.id)
            .first()
        )
        if notification:
            return notification
        raise Exception(f"Notification {notification_id} not found")

    @staticmethod
    def edit_notification(notification: Notification):
        notification = DataBase.get_notification(notification.id)
        if notification:
            db.session.merge(notification)
            db.session.commit()
        else:
            raise Exception(f"Notification {notification.id} not found")

    @staticmethod
    def delete_notification(notification: Notification):
        notification = DataBase.get_notification(notification.id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
        else:
            raise Exception(f"Notification {notification.id} not found")

    @staticmethod
    def get_notifications() -> List[Notification]:
        current_user = DataBase.get_current_user()
        notifications = (
            db.session.query(Notification)
            .filter_by(user=current_user.id)
            .all()
        )
        return notifications

    """--------------------------- INTERNAL ACCESS ---------------------------"""

    @staticmethod
    def get_user(username: str):
        return db.session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_website_by_id(website_id: int) -> Website:
        website = (
            db.session.query(Website)
            .filter_by(id=website_id)
            .first()
        )
        if website:
            return website
        raise Exception(f"Website {website_id} not found")

    @staticmethod
    def get_notifications_all_users() -> List[Notification]:
        return db.session.query(Notification).all()

    @staticmethod
    def get_notifications_for_user(action_history: ActionHistory) -> List[Notification]:
        user_id = db.session.query(Website).filter_by(id=action_history.website).first().user
        return (db.session.query(Notification)
                .filter_by(user=user_id)
                .filter(Notification._triggers.like(f"%{action_history.execution_status.value}%"))
                .all())

    @staticmethod
    def get_websites_all_users() -> List[Website]:
        return db.session.scalars(db.select(Website)).all()

    @staticmethod
    def get_website_all_users(website_id: int) -> Website:
        return db.session.get(Website, website_id)

    @staticmethod
    def action_history_finish_execution(action_history_id: int, execution_status: ActionStatusCode,
                                        failed_details: ActionFailedDetails, screenshot_id: str = None):
        existing_action_history = db.session.get(ActionHistory, action_history_id)
        if existing_action_history is None:
            return
        existing_action_history.execution_ended = datetime.now(timezone.utc)
        existing_action_history.execution_status = execution_status
        existing_action_history.failed_details = failed_details
        existing_action_history.screenshot_id = screenshot_id
        db.session.commit()

    @staticmethod
    def unexpected_execution_failure(website_id: int, execution_started: datetime) -> List[int]:
        running_action_histories = db.session.query(ActionHistory).filter(
            ActionHistory.execution_status == ActionStatusCode.IN_PROGRESS,
            ActionHistory.website == website_id
        ).all()
        action_history_ids = []
        for action_history in running_action_histories:
            action_history.execution_status = ActionStatusCode.FAILED
            action_history.execution_ended = datetime.now(timezone.utc)
            action_history.failed_details = ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
            action_history_ids.append(action_history.id)
        if len(running_action_histories) == 0:
            action_history_id = DataBase.add_action_history(website_id,
                                                            ActionHistory(
                                                                execution_status=ActionStatusCode.FAILED,
                                                                execution_started=execution_started,
                                                                execution_ended=datetime.now(timezone.utc),
                                                                failed_details=ActionFailedDetails.UNKNOWN_EXECUTION_ERROR))
            action_history_ids.append(action_history_id)
        db.session.commit()
        return action_history_ids

    @staticmethod
    def add_action_history(website_id: int, action_history: ActionHistory) -> int:
        website = db.session.get(Website, website_id)
        website.action_histories.append(action_history)
        if website.paused:
            website.next_schedule = None  # In order to prevent race conditions
        else:
            website.next_schedule = website.action_interval.get_random_action_datetime()
        db.session.commit()
        return action_history.id

