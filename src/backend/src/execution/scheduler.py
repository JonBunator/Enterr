from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask import Flask

from database.change_database import IDataBase
from database.database import ActionHistory
from execution.login.find_form_automatically import XPaths, XPath
from execution.login.login import LoginStatusCode, random_login


def login_task(app: Flask, website_id: int, url: str, username: str, password: str, x_paths: XPaths = None) -> LoginStatusCode:
    with app.app_context():
        start_time = datetime.now()

        # login
        status = random_login(url=url, username=username, password=password, x_paths=x_paths)
        executions_status = LoginStatusCode.SUCCESS
        failed_details = None
        if status != LoginStatusCode.SUCCESS:
            executions_status = LoginStatusCode.FAILED
            if executions_status != LoginStatusCode.FAILED:
                failed_details = executions_status.value

        action_history = ActionHistory(
            execution_started=start_time,
            execution_ended=datetime.now(),
            execution_status=executions_status.value,
            failed_details=failed_details,
        )
        print(website_id)
        IDataBase.add_action_history(website_id=website_id, action_history=action_history)

class Scheduler:
    def __init__(self, app: Flask):
        self.scheduler = BackgroundScheduler()
        self.app = app

    def start(self):
        self._refresh_tasks()
        self.scheduler.start()

    def add_task(self, website_id: int):
        pass

    def _refresh_tasks(self):
        for website in IDataBase.get_all_websites():
            url = website.url
            print(url)
            username = website.username
            password = website.password
            x_paths = None
            print(IDataBase.get_action_history(website=website))
            if website.custom_access is not None:
                access = website.custom_access
                x_paths = XPaths(
                    username=XPath(access.username_xpath),
                    password=XPath(access.password_xpath),
                    submit_button=XPath(access.submit_button_xpath))
            if website.next_schedule is not None:
                action_time = website.next_schedule
            else:
                action_time = website.action_interval.get_random_action_datetime()
                IDataBase.schedule_website_login(website, action_time)
            self.scheduler.add_job(
                login_task,
                trigger=DateTrigger(run_date=action_time),
                args=[self.app, website.id, url, username, password, x_paths],
                id=f"login_{website.id}",
                replace_existing=True,
                misfire_grace_time=3600
            )
