from datetime import datetime, timedelta, timezone

import pytest
from apscheduler.jobstores.base import JobLookupError

from dataAccess.data_access_internal import DataAccessInternal
from dataAccess.database.database import (
    ActionFailedDetails,
    ActionStatusCode,
    Website,
)
from execution.login.constants import LoginStatusCode
from execution.scheduler import Scheduler


def _website(**overrides) -> Website:
    values = dict(
        id=5,
        url="https://example.com/login",
        success_url="https://example.com/home",
        name="Example",
        username="alice",
        password="secret",
        custom_login_script=None,
        take_screenshot=False,
        paused=False,
        next_schedule=None,
    )
    values.update(overrides)
    return Website(**values)


@pytest.fixture
def data_access(mocker):
    data_access = mocker.Mock(spec=DataAccessInternal)
    data_access.add_action_history.return_value = 42
    return data_access


@pytest.fixture
def scheduler(data_access, webhooks, mocker):
    scheduler = Scheduler(data_access_internal=data_access, webhook_endpoints=webhooks)
    mocker.patch.object(scheduler.scheduler, "add_job")
    mocker.patch.object(scheduler.scheduler, "remove_job")
    return scheduler


@pytest.fixture
def get_website(mocker):
    return mocker.patch.object(DataAccessInternal, "get_website_all_users")


# ---------------------------- add / remove ----------------------------


def _scheduled_run_date(scheduler):
    scheduler.scheduler.add_job.assert_called_once()
    kwargs = scheduler.scheduler.add_job.call_args.kwargs
    assert kwargs["id"] == "5"
    assert kwargs["args"] == [5]
    return kwargs["trigger"].run_date


def test_add_task_without_schedule_runs_now(scheduler, get_website):
    get_website.return_value = _website()
    before = datetime.now(timezone.utc)

    scheduler.add_task(5)

    run_date = _scheduled_run_date(scheduler)
    assert before <= run_date <= datetime.now(timezone.utc)


def test_add_task_paused_without_schedule_is_skipped(scheduler, get_website):
    get_website.return_value = _website(paused=True)

    scheduler.add_task(5)

    scheduler.scheduler.add_job.assert_not_called()


def test_add_task_in_future_uses_next_schedule(scheduler, get_website):
    next_schedule = datetime.now() + timedelta(days=1)  # naive, as stored in the DB
    get_website.return_value = _website(next_schedule=next_schedule)

    scheduler.add_task(5)

    assert _scheduled_run_date(scheduler) == next_schedule.replace(
        tzinfo=timezone.utc
    )


def test_add_task_in_past_runs_now(scheduler, get_website):
    get_website.return_value = _website(next_schedule=datetime(2020, 1, 1))
    before = datetime.now(timezone.utc)

    scheduler.add_task(5)

    run_date = _scheduled_run_date(scheduler)
    assert before <= run_date <= datetime.now(timezone.utc)


def test_remove_task(scheduler):
    scheduler.remove_task(5)
    scheduler.scheduler.remove_job.assert_called_once_with(job_id="5")


def test_remove_unknown_task_does_not_raise(scheduler):
    scheduler.scheduler.remove_job.side_effect = JobLookupError("5")
    scheduler.remove_task(5)


# ---------------------------- login task ----------------------------


def test_login_task_success(scheduler, data_access, get_website, mocker):
    get_website.return_value = _website()
    login = mocker.patch(
        "execution.scheduler.login", return_value=(LoginStatusCode.SUCCESS, None)
    )

    scheduler._login_task(5)

    data_access.set_next_schedule.assert_called_once_with(5)
    add_kwargs = data_access.add_action_history.call_args.kwargs
    assert add_kwargs["website_id"] == 5
    assert add_kwargs["action_history"].execution_status == ActionStatusCode.IN_PROGRESS
    login.assert_called_once_with(
        url="https://example.com/login",
        success_url="https://example.com/home",
        username="alice",
        password="secret",
        custom_login_script=None,
        screenshot_id=None,
    )
    data_access.action_history_finish_execution.assert_called_once_with(
        action_history_id=42,
        execution_status=ActionStatusCode.SUCCESS,
        failed_details=None,
        custom_failed_details_message=None,
        screenshot_id=None,
    )


def test_login_task_failure(scheduler, data_access, get_website, mocker):
    get_website.return_value = _website()
    mocker.patch(
        "execution.scheduler.login",
        return_value=(LoginStatusCode.PASSWORD_FIELD_NOT_FOUND, "details"),
    )

    scheduler._login_task(5)

    data_access.action_history_finish_execution.assert_called_once_with(
        action_history_id=42,
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND,
        custom_failed_details_message="details",
        screenshot_id=None,
    )


def test_login_task_with_screenshot(scheduler, data_access, get_website, mocker):
    get_website.return_value = _website(take_screenshot=True)
    login = mocker.patch(
        "execution.scheduler.login", return_value=(LoginStatusCode.SUCCESS, None)
    )

    scheduler._login_task(5)

    screenshot_id = login.call_args.kwargs["screenshot_id"]
    assert screenshot_id is not None
    finish_kwargs = data_access.action_history_finish_execution.call_args.kwargs
    assert finish_kwargs["screenshot_id"] == screenshot_id


def test_job_error_marks_execution_as_failed(scheduler, data_access, mocker):
    started = datetime(2024, 5, 10, 8, 0, tzinfo=timezone.utc)
    event = mocker.Mock(
        exception=RuntimeError("boom"), job_id="5", scheduled_run_time=started
    )

    scheduler._scheduler_event(event)

    data_access.unexpected_execution_failure.assert_called_once_with(
        website_id="5", execution_started=started
    )
