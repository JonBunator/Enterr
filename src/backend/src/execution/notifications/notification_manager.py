from datetime import datetime, timezone

import apprise

from dataAccess.database.database import ActionHistory


class NotificationManager:
    def __init__(self):
        self.notifier = apprise.Apprise()
        self.database_access = None

    def add_notification(self, notifier: str, title: str, body: str):
        notification_id = str(datetime.now(timezone.utc))
        self.database_access.add_notification(notification_id, notifier, title, body)
        self.notifier.add(notifier, tag=notification_id)

    def notify(self, action_history_id: str):
        for notification in self.database_access.get_notifications():
            action_history = self.database_access.get_action_history(action_history_id)
            title = NotificationManager._replace_variables(notification.title, action_history)
            body = NotificationManager._replace_variables(notification.body, action_history)
            self.notifier.notify(
                title=title,
                body=body,
                tag=notification.notification_id
            )

    @staticmethod
    def _replace_variables(value: str, action_history: ActionHistory) -> str:
        return value
