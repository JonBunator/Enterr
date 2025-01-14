import uuid
from datetime import datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask import Flask
from dataAccess.data_access import DataAccess
from dataAccess.database.database import ActionHistory, ActionStatusCode
from execution.login.find_form_automatically import XPaths, XPath
from execution.login.login import LoginStatusCode, login


class Scheduler:
    def __init__(self, app: Flask, data_access: DataAccess):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.data_access = data_access

    def start(self):
        self._init_tasks()
        self.scheduler.start()

    def _init_tasks(self):
        for website in DataAccess.get_all_websites():
            self.add_task(website.id)

    def _login_task(self, website_id: int):
        screenshot_id = None
        with self.app.app_context():
            website = DataAccess.get_website(website_id)
            if website.take_screenshot:
                screenshot_id = str(uuid.uuid4())
            start_time = datetime.now()
            url = website.url
            success_url = website.success_url
            username = website.username
            password = website.password
            x_paths = None
            if website.custom_access is not None:
                access = website.custom_access
                x_paths = XPaths(
                    username=XPath(access.username_xpath),
                    password=XPath(access.password_xpath),
                    submit_button=XPath(access.submit_button_xpath))

            action_history = ActionHistory(
                execution_started=start_time,
                execution_status=ActionStatusCode.IN_PROGRESS,
            )
            action_history_id = self.data_access.add_action_history(website_id=website.id, action_history=action_history)
        # login
        status = login(url=url, success_url=success_url, username=username, password=password, x_paths=x_paths, screenshot_id=screenshot_id)

        executions_status = LoginStatusCode.SUCCESS
        failed_details = None
        if status != LoginStatusCode.SUCCESS:
            executions_status = LoginStatusCode.FAILED
            if executions_status != LoginStatusCode.FAILED:
                failed_details = executions_status.value

        with self.app.app_context():
            self.data_access.action_history_finish_execution(action_history_id=action_history_id,
                                                     execution_status=ActionStatusCode(executions_status.value),
                                                     failed_details=failed_details,
                                                     screenshot_id=screenshot_id)



    def add_task(self, website_id: int):
        website = DataAccess.get_website(website_id)
        if website.next_schedule is None:
            return
        self.scheduler.add_job(
            self._login_task,
            trigger=DateTrigger(run_date=website.next_schedule),
            args=[website_id],
            id=f"login_{website_id}",
            replace_existing=True,
            coalesce=True,
        )

    def remove_task(self, website_id: int):
        try:
            self.scheduler.remove_job(job_id=f"login_{website_id}")
        except JobLookupError:
            print(f"Error removing job with id login_{website_id}")