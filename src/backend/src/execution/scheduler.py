import asyncio
import uuid
from datetime import datetime
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.date import DateTrigger
from dataAccess.data_access_internal import DataAccessInternal
from dataAccess.database.database import ActionHistory, ActionStatusCode, get_session
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from execution.login.find_form_automatically import XPaths, XPath
from execution.login.login import LoginStatusCode, login


class Scheduler:
    def __init__(self, data_access_internal: DataAccessInternal):
        self.scheduler = AsyncIOScheduler()
        self.data_access = data_access_internal

    def start(self):
        self._init_tasks()
        self.scheduler.add_listener(self._scheduler_event, EVENT_JOB_ERROR)
        self.scheduler.start()

    def _scheduler_event(self, event: JobExecutionEvent):
        if event.exception:
            self.data_access.unexpected_execution_failure(website_id=event.job_id,
                                                          execution_started=event.scheduled_run_time)

    def _init_tasks(self):
        for website in DataAccessInternal.get_websites_all_users():
            self.add_task(website.id)

    async def _login_task(self, website_id: int):
        screenshot_id = None
        website = DataAccessInternal.get_website_all_users(website_id)
        if website.take_screenshot:
            screenshot_id = str(uuid.uuid4())
        start_time = datetime.now()
        url = website.url
        success_url = website.success_url
        username = website.username
        password = website.password
        pin = website.pin
        x_paths = None
        if website.custom_access is not None:
            access = website.custom_access
            x_paths = XPaths(
                username=XPath(access.username_xpath),
                password=XPath(access.password_xpath),
                pin=XPath(access.pin_xpath),
                submit_button=XPath(access.submit_button_xpath))

        action_history = ActionHistory(
            execution_started=start_time,
            execution_status=ActionStatusCode.IN_PROGRESS,
        )
        action_history_id = self.data_access.add_action_history(website_id=website.id,
                                                                      action_history=action_history)
        await WebhookEndpoints.action_history_changed_async(action_history_id=action_history_id)
        # login
        status = login(url=url, success_url=success_url, username=username, password=password, pin=pin, x_paths=x_paths,
                       screenshot_id=screenshot_id)
        executions_status = LoginStatusCode.SUCCESS
        failed_details = None
        if status != LoginStatusCode.SUCCESS:
            executions_status = LoginStatusCode.FAILED
            failed_details = status.value

        self.data_access.action_history_finish_execution(action_history_id=action_history_id,
                                                               execution_status=ActionStatusCode(
                                                                   executions_status.value),
                                                               failed_details=failed_details,
                                                               screenshot_id=screenshot_id)

    def add_task(self, website_id: int):
        website = DataAccessInternal.get_website_all_users(website_id)
        if website.next_schedule is None:
            return

        if website.next_schedule < datetime.now():
            run_date = datetime.now()
        else:
            run_date = website.next_schedule
        self.scheduler.add_job(
            self._login_task,
            trigger=DateTrigger(run_date=run_date),
            args=[website_id],
            id=f"{website_id}",
            replace_existing=True,
            coalesce=True,
            misfire_grace_time=3600
        )

    def remove_task(self, website_id: int):
        try:
            self.scheduler.remove_job(job_id=f"{website_id}")
        except JobLookupError:
            print(f"Error removing job with id {website_id}")
