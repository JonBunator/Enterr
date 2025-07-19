from datetime import datetime, timedelta
import apprise
from enum import Enum
from dataAccess.data_access_internal import DataAccessInternal
from dataAccess.database.database import ActionHistory, Notification, ActionStatusCode, ActionFailedDetails, get_session


class NotificationVariable(Enum):
    STATUS = "STATUS"
    STATUS_MESSAGE = "STATUS_MESSAGE"
    EXECUTION_STARTED_DATETIME = "EXECUTION_STARTED_DATETIME"
    EXECUTION_ENDED_DATETIME = "EXECUTION_ENDED_DATETIME"
    EXECUTION_STARTED_TIME_MESSAGE = "EXECUTION_STARTED_TIME_MESSAGE"
    EXECUTION_ENDED_TIME_MESSAGE = "EXECUTION_ENDED_TIME_MESSAGE"
    EXECUTION_DATE_MESSAGE = "EXECUTION_DATE_MESSAGE"
    FAILED_DETAILS = "FAILED_DETAILS"
    FAILED_DETAILS_MESSAGE = "FAILED_DETAILS_MESSAGE"
    SCREENSHOT_ID = "SCREENSHOT_ID"
    WEBSITE_NAME = "WEBSITE_NAME"
    WEBSITE_URL = "WEBSITE_URL"


class NotificationManager:
    def __init__(self, data_access: DataAccessInternal):
        self.notifier = apprise.Apprise()
        self.data_access = data_access
        self._init_notifications()

    def _init_notifications(self):
        for notification in self.data_access.get_notifications_all_users():
            self.add_notification(notification)

    def add_notification(self, notification: Notification):
        self.notifier.add(notification.apprise_token, tag=str(notification.id))

    def test_notification(self, notification: Notification):
        self.notifier.add(notification.apprise_token, tag=str(notification.id))
        title = NotificationManager._replace_fake_variables(notification.title)
        body = NotificationManager._replace_fake_variables(notification.body)
        self.notifier.notify(title=title,
                             body=body,
                             tag=str(notification.id))
        self.updated_notifications()

    def updated_notifications(self):
        self.notifier.clear()
        self._init_notifications()

    def notify(self, action_history: ActionHistory):
        for notification in self.data_access.get_notifications_for_user(action_history):
            title = NotificationManager._replace_variables(notification.title, action_history)
            body = NotificationManager._replace_variables(notification.body, action_history)
            self.notifier.notify(
                title=title,
                body=body,
                tag=str(notification.id),
            )

    @staticmethod
    def _get_status_message(action_history: ActionHistory) -> str:
        if action_history.execution_status == ActionStatusCode.SUCCESS:
            return "Login successful"
        elif action_history.execution_status == ActionStatusCode.FAILED:
            return "Login failed"
        elif action_history.execution_status == ActionStatusCode.IN_PROGRESS:
            return "In Progress"
        else:
            return "Unknown"

    @staticmethod
    def _get_failed_details_message(action_history: ActionHistory) -> str:

        if action_history.failed_details is None:
            return "No error details available"

        failed_details_messages = {
            ActionFailedDetails.AUTOMATIC_FORM_DETECTION_FAILED:
                "Automatic form detection failed",
            ActionFailedDetails.USERNAME_FIELD_NOT_FOUND:
                "Username field not found",
            ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND:
                "Password field not found",
            ActionFailedDetails.PIN_FIELD_NOT_FOUND:
                "PIN field not found",
            ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND:
                "Submit button not found",
            ActionFailedDetails.SUCCESS_URL_DID_NOT_MATCH:
                "The success url did not match after login attempt",
            ActionFailedDetails.UNKNOWN_EXECUTION_ERROR:
                "An unknown error occurred while executing task"
        }

        return failed_details_messages.get(action_history.failed_details, "Unknown error")

    @staticmethod
    def _get_variable(variable: NotificationVariable) -> str:
        return "{" + str(variable.value) + "}"

    @staticmethod
    def _replace_variables(value: str, action_history: ActionHistory) -> str:
        value = value.replace(NotificationManager._get_variable(NotificationVariable.STATUS),
                              action_history.execution_status.value)
        value = value.replace(NotificationManager._get_variable(NotificationVariable.STATUS_MESSAGE),
                              NotificationManager._get_status_message(action_history))

        # Execution time replacements
        # Datetimes
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_STARTED_DATETIME),
                              str(action_history.execution_started))

        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_ENDED_DATETIME),
                              str(action_history.execution_ended) if action_history.execution_ended else "null")

        # Started

        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_STARTED_TIME_MESSAGE),
                              action_history.execution_started.strftime("%H:%M:%S"))

        # Ended
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_ENDED_TIME_MESSAGE),
                              action_history.execution_ended.strftime(
                                  "%H:%M:%S") if action_history.execution_ended else "Not ended yet")

        # Date
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_DATE_MESSAGE),
                              action_history.execution_started.strftime("%Y-%m-%d"))

        # Failed details replacements
        value = value.replace(NotificationManager._get_variable(NotificationVariable.FAILED_DETAILS),
                              str(action_history.failed_details.value) if action_history.failed_details else "null")
        value = value.replace(NotificationManager._get_variable(NotificationVariable.FAILED_DETAILS_MESSAGE),
                              NotificationManager._get_failed_details_message(action_history))

        # Screenshot replacement
        value = value.replace(NotificationManager._get_variable(NotificationVariable.SCREENSHOT_ID),
                              str(action_history.screenshot_id) if action_history.screenshot_id else "null")

        # Website info replacements
        website = DataAccessInternal.get_website_by_id(action_history.website, session)
        value = value.replace(NotificationManager._get_variable(NotificationVariable.WEBSITE_NAME), website.name)
        value = value.replace(NotificationManager._get_variable(NotificationVariable.WEBSITE_URL), website.url)
        return value

    @staticmethod
    def _replace_fake_variables(value: str) -> str:
        value = value.replace(NotificationManager._get_variable(NotificationVariable.STATUS),
                              "FAILED")
        value = value.replace(NotificationManager._get_variable(NotificationVariable.STATUS_MESSAGE),
                              "Login failed")

        # Execution time replacements
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)

        # Datetimes
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_STARTED_DATETIME),
                              str(start_time))

        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_ENDED_DATETIME),
                              str(end_time))

        # Started
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_STARTED_TIME_MESSAGE),
                              start_time.strftime("%H:%M:%S"))

        # Ended
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_ENDED_TIME_MESSAGE),
                              end_time.strftime("%H:%M:%S"))

        # Date
        value = value.replace(NotificationManager._get_variable(NotificationVariable.EXECUTION_DATE_MESSAGE),
                              start_time.strftime("%Y-%m-%d"))

        # Failed details replacements
        value = value.replace(NotificationManager._get_variable(NotificationVariable.FAILED_DETAILS),
                              "PASSWORD_FIELD_NOT_FOUND")
        value = value.replace(NotificationManager._get_variable(NotificationVariable.FAILED_DETAILS_MESSAGE),
                              "Password field not found")

        # Screenshot replacement
        value = value.replace(NotificationManager._get_variable(NotificationVariable.SCREENSHOT_ID), "17d0b186-790a-4f4a-93d5-80524d05019a")

        # Website info replacements
        value = value.replace(NotificationManager._get_variable(NotificationVariable.WEBSITE_NAME), "My awesome website")
        value = value.replace(NotificationManager._get_variable(NotificationVariable.WEBSITE_URL), "https://www.example.com/login")
        return value
