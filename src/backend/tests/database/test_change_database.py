from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from dataAccess.database.change_database import DataBase
from dataAccess.database.database import (
    ActionFailedDetails,
    ActionHistory,
    ActionInterval,
    ActionStatusCode,
    Notification,
    Website,
)
from utils.exceptions import NotFoundException
from utils.security import create_access_token


def _new_website(**overrides) -> Website:
    values = dict(
        url="https://example.com/login",
        success_url="https://example.com/home",
        name="Example",
        username="user123",
        password="password123",
        added_at=datetime(2020, 1, 1),
        take_screenshot=False,
        paused=False,
    )
    values.update(overrides)
    return Website(**values)


def _add_history(session, website, status, started=None) -> ActionHistory:
    action_history = ActionHistory(
        execution_started=started or datetime(2024, 5, 10, 8, 0),
        execution_status=status,
        website=website.id,
    )
    session.add(action_history)
    session.commit()
    return action_history


# ---------------------------- USER ----------------------------


def test_get_current_user_valid_token(user):
    current_user = DataBase.get_current_user(create_access_token(user.username))
    assert current_user.id == user.id


@pytest.mark.parametrize("token_type", ["invalid", "unknown_user"])
def test_get_current_user_invalid_token_raises_401(session, token_type):
    if token_type == "invalid":
        token = "invalid-token"
    else:
        token = create_access_token("unknown-user")

    with pytest.raises(HTTPException) as exc:
        DataBase.get_current_user(token)
    assert exc.value.status_code == 401


# ---------------------------- WEBSITES ----------------------------


def test_add_website_sets_owner_and_schedules_it(session, user):
    website = DataBase.add_website(_new_website(), user)

    assert website.id is not None
    assert website.user == user.id
    assert website.next_schedule is not None


def test_add_paused_website_is_not_scheduled(session, user):
    website = DataBase.add_website(_new_website(paused=True), user)
    assert website.next_schedule is None


def test_get_website_of_other_user_raises(make_website, other_user):
    website = make_website()

    assert DataBase.get_website(website.id, website.parent_user).id == website.id
    with pytest.raises(NotFoundException):
        DataBase.get_website(website.id, other_user)


def test_delete_website(session, make_website, user):
    website = make_website()

    DataBase.delete_website(website.id, user)

    assert session.query(Website).count() == 0


def test_delete_website_of_other_user_raises(session, make_website, other_user):
    website = make_website()

    with pytest.raises(NotFoundException):
        DataBase.delete_website(website.id, other_user)
    assert session.query(Website).count() == 1


def test_trigger_login_sets_next_schedule(session, make_website, user, other_user):
    website = make_website(next_schedule=datetime(2099, 1, 1))

    with pytest.raises(NotFoundException):
        DataBase.trigger_login(website.id, other_user)

    DataBase.trigger_login(website.id, user)

    session.refresh(website)
    assert website.next_schedule < datetime(2099, 1, 1)


# ---------------------------- SCHEDULING ----------------------------


def test_set_next_schedule_uses_random_action_datetime(session, make_website, mocker):
    next_schedule = datetime(2030, 1, 1, 12, 0)
    mocker.patch.object(
        ActionInterval, "get_random_action_datetime", return_value=next_schedule
    )
    website = make_website()

    DataBase.set_next_schedule(website.id)

    session.expire_all()
    assert session.get(Website, website.id).next_schedule == next_schedule


def test_set_next_schedule_paused_clears_schedule(session, make_website):
    website = make_website(paused=True, next_schedule=datetime(2030, 1, 1))

    DataBase.set_next_schedule(website.id)

    session.expire_all()
    assert session.get(Website, website.id).next_schedule is None


def test_set_next_schedule_unknown_website_raises(session):
    with pytest.raises(NotFoundException):
        DataBase.set_next_schedule(999)


# ---------------------------- ACTION HISTORY ----------------------------


def test_add_and_finish_action_history(session, make_website):
    website = make_website()
    action_history = DataBase.add_action_history(
        website.id,
        ActionHistory(
            execution_started=datetime.now(timezone.utc),
            execution_status=ActionStatusCode.IN_PROGRESS,
        ),
    )

    website_id = DataBase.action_history_finish_execution(
        action_history.id,
        ActionStatusCode.FAILED,
        ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND,
        "custom message",
        "screenshot-id",
    )

    assert website_id == website.id
    stored = session.get(ActionHistory, action_history.id)
    assert stored.execution_status == ActionStatusCode.FAILED
    assert stored.execution_ended is not None
    assert stored.failed_details == ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND
    assert stored.custom_failed_details_message == "custom message"
    assert stored.screenshot_id == "screenshot-id"


def test_finish_unknown_action_history_returns_none(session):
    assert (
        DataBase.action_history_finish_execution(999, ActionStatusCode.SUCCESS, None)
        is None
    )


def test_unexpected_execution_failure_marks_running_histories_failed(
    session, make_website
):
    website = make_website()
    running = _add_history(session, website, ActionStatusCode.IN_PROGRESS)
    _add_history(session, website, ActionStatusCode.SUCCESS)

    ids = DataBase.unexpected_execution_failure(website.id, datetime.now())

    assert ids == [running.id]
    session.expire_all()
    stored = session.get(ActionHistory, running.id)
    assert stored.execution_status == ActionStatusCode.FAILED
    assert stored.failed_details == ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
    assert session.query(ActionHistory).count() == 2


def test_unexpected_execution_failure_creates_failed_history(session, make_website):
    website = make_website()
    started = datetime(2024, 5, 10, 8, 0)

    ids = DataBase.unexpected_execution_failure(website.id, started)

    assert len(ids) == 1
    stored = session.get(ActionHistory, ids[0])
    assert stored.website == website.id
    assert stored.execution_started == started
    assert stored.execution_status == ActionStatusCode.FAILED
    assert stored.failed_details == ActionFailedDetails.UNKNOWN_EXECUTION_ERROR


def test_get_last_successful_login(session, make_website, user, other_user):
    website = make_website()
    _add_history(session, website, ActionStatusCode.SUCCESS, datetime(2024, 1, 1))
    latest = _add_history(
        session, website, ActionStatusCode.SUCCESS, datetime(2024, 2, 1)
    )
    _add_history(session, website, ActionStatusCode.FAILED, datetime(2024, 3, 1))

    assert DataBase.get_last_successful_login(website.id, user).id == latest.id
    with pytest.raises(NotFoundException):
        DataBase.get_last_successful_login(website.id, other_user)


def test_get_action_history(session, make_website, user, other_user):
    website = make_website()
    action_history = _add_history(session, website, ActionStatusCode.SUCCESS)

    assert DataBase.get_action_history(action_history.id, user).id == action_history.id
    with pytest.raises(NotFoundException):
        DataBase.get_action_history(action_history.id, other_user)
    with pytest.raises(NotFoundException):
        DataBase.get_action_history(999, user)


# ---------------------------- NOTIFICATIONS ----------------------------


def _add_notification(session, user, triggers) -> Notification:
    notification = Notification(
        name="n", apprise_token="json://localhost", title="t", body="b", user=user.id
    )
    notification.triggers = triggers
    session.add(notification)
    session.commit()
    return notification


def test_get_notifications_for_user_filters_by_trigger(
    session, make_website, user, other_user
):
    website = make_website()
    failed_notification = _add_notification(
        session, user, [ActionStatusCode.FAILED, ActionStatusCode.SUCCESS]
    )
    _add_notification(session, user, [ActionStatusCode.SUCCESS])
    _add_notification(session, other_user, [ActionStatusCode.FAILED])
    action_history = _add_history(session, website, ActionStatusCode.FAILED)

    notifications = DataBase.get_notifications_for_user(action_history)

    assert [n.id for n in notifications] == [failed_notification.id]


def test_get_notification_of_other_user_raises(session, user, other_user):
    notification = _add_notification(session, user, [ActionStatusCode.FAILED])

    assert DataBase.get_notification(notification.id, user).id == notification.id
    with pytest.raises(NotFoundException):
        DataBase.get_notification(notification.id, other_user)
