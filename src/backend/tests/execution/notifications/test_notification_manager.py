from datetime import datetime

import pytest

from dataAccess.data_access_internal import DataAccessInternal
from dataAccess.database.database import (
    ActionFailedDetails,
    ActionHistory,
    ActionStatusCode,
    Notification,
    Website,
)
from execution.notifications.notification_manager import NotificationManager

ALL_VARIABLES = (
    "{STATUS}|{STATUS_MESSAGE}|{EXECUTION_STARTED_DATETIME}|{EXECUTION_ENDED_DATETIME}|"
    "{EXECUTION_STARTED_TIME_MESSAGE}|{EXECUTION_ENDED_TIME_MESSAGE}|{EXECUTION_DATE_MESSAGE}|"
    "{FAILED_DETAILS}|{FAILED_DETAILS_MESSAGE}|{SCREENSHOT_ID}|{WEBSITE_NAME}|{WEBSITE_URL}"
)


def _notification(notification_id: int) -> Notification:
    notification = Notification(
        id=notification_id,
        name=f"notification {notification_id}",
        apprise_token=f"json://localhost/{notification_id}",
        title="{WEBSITE_NAME}: {STATUS}",
        body="{FAILED_DETAILS_MESSAGE}",
    )
    notification.triggers = [ActionStatusCode.FAILED]
    return notification


@pytest.fixture
def notifier(mocker):
    apprise_cls = mocker.patch(
        "execution.notifications.notification_manager.apprise.Apprise"
    )
    return apprise_cls.return_value


@pytest.fixture(autouse=True)
def website(mocker):
    return mocker.patch.object(
        DataAccessInternal,
        "get_website_by_id",
        return_value=Website(name="My site", url="https://my.site"),
    )


@pytest.fixture
def data_access(mocker):
    data_access = mocker.Mock(spec=DataAccessInternal)
    data_access.get_notifications_all_users.return_value = [
        _notification(1),
        _notification(2),
    ]
    return data_access


@pytest.fixture
def manager(notifier, data_access):
    return NotificationManager(data_access=data_access)


def test_replace_variables_failed_execution():
    action_history = ActionHistory(
        execution_started=datetime(2024, 5, 10, 8, 15, 30),
        execution_ended=datetime(2024, 5, 10, 8, 16, 0),
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND,
        custom_failed_details_message="extra info",
        screenshot_id="abc",
        website=7,
    )

    result = NotificationManager._replace_variables(ALL_VARIABLES, action_history)

    assert result == (
        "FAILED|Login failed|2024-05-10 08:15:30|2024-05-10 08:16:00|"
        "08:15:30|08:16:00|2024-05-10|"
        "PASSWORD_FIELD_NOT_FOUND|Password field not found extra info|abc|My site|https://my.site"
    )


def test_replace_variables_without_optional_values(website):
    action_history = ActionHistory(
        execution_started=datetime(2024, 5, 10, 8, 15, 30),
        execution_status=ActionStatusCode.IN_PROGRESS,
        website=7,
    )

    result = NotificationManager._replace_variables(ALL_VARIABLES, action_history)

    assert result == (
        "IN_PROGRESS|In Progress|2024-05-10 08:15:30|null|"
        "08:15:30|Not ended yet|2024-05-10|"
        "null|No error details available|null|My site|https://my.site"
    )
    website.assert_called_once_with(7)


def test_replace_fake_variables_replaces_everything():
    result = NotificationManager._replace_fake_variables(ALL_VARIABLES)
    assert "{" not in result
    assert result.startswith("FAILED|Login failed|")


def test_init_registers_all_notifications(manager, notifier):
    assert notifier.add.call_args_list == [
        (("json://localhost/1",), {"tag": "1"}),
        (("json://localhost/2",), {"tag": "2"}),
    ]


def test_updated_notifications_reloads(manager, notifier, data_access):
    data_access.get_notifications_all_users.return_value = [_notification(3)]
    notifier.reset_mock()

    manager.updated_notifications()

    notifier.clear.assert_called_once()
    notifier.add.assert_called_once_with("json://localhost/3", tag="3")


def test_notify_sends_to_matching_notifications(manager, notifier, data_access):
    data_access.get_notifications_for_user.return_value = [
        _notification(1),
        _notification(2),
    ]
    action_history = ActionHistory(
        execution_started=datetime(2024, 5, 10, 8, 15, 30),
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND,
        website=7,
    )

    manager.notify(action_history)

    data_access.get_notifications_for_user.assert_called_once_with(action_history)
    assert notifier.notify.call_args_list == [
        ((), {"title": "My site: FAILED", "body": "Submit button not found", "tag": "1"}),
        ((), {"title": "My site: FAILED", "body": "Submit button not found", "tag": "2"}),
    ]


def test_test_notification_sends_with_fake_values(manager, notifier):
    manager.test_notification(_notification(9))

    notifier.add.assert_any_call("json://localhost/9", tag="9")
    notifier.notify.assert_called_once_with(
        title="My awesome website: FAILED", body="Password field not found", tag="9"
    )
