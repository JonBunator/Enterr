from datetime import datetime, timezone
from typing import List

from dataAccess.database.database import Website, _db as db, ActionHistory, ActionFailedDetails, ActionStatusCode


class DataBase:
    @staticmethod
    def get_all_websites() -> List[Website]:
        return db.session.scalars(db.select(Website)).all()

    @staticmethod
    def get_website(website_id: int) -> Website:
        return db.session.get(Website, website_id)

    @staticmethod
    def add_website(website: Website):
        website.next_schedule = datetime.now(timezone.utc)
        db.session.add(website)
        db.session.commit()

    @staticmethod
    def edit_website(website: Website):
        db.session.merge(website)
        db.session.commit()

    @staticmethod
    def delete_website(website: Website):
        db.session.delete(website)
        db.session.commit()

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
    def trigger_login(website_id: int):
        website = db.session.get(Website, website_id)
        website.next_schedule = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def get_action_history(website: Website) -> List[ActionHistory]:
        return sorted(website.action_histories, key=lambda ah: ah.execution_started, reverse=True)
