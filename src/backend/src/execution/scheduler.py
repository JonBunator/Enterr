from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask import Flask
from database.change_database import IDataBase
from database.database import ActionHistory, Website
from execution.login.find_form_automatically import XPaths, XPath
from execution.login.login import LoginStatusCode, random_login, login


class Scheduler:
    def __init__(self, app: Flask):
        self.scheduler = BackgroundScheduler()
        self.app = app

    def start(self):
        self._init_tasks()
        self.scheduler.start()

    def _init_tasks(self):
        for website in IDataBase.get_all_websites():
            self.add_task(website.id)

    def _login_task(self, website_id: int):
        with self.app.app_context():
            website = IDataBase.get_website(website_id)
            start_time = datetime.now()
            url = website.url
            username = website.username
            password = website.password
            x_paths = None
            if website.custom_access is not None:
                access = website.custom_access
                x_paths = XPaths(
                    username=XPath(access.username_xpath),
                    password=XPath(access.password_xpath),
                    submit_button=XPath(access.submit_button_xpath))

            # login
            status = login(url=url, username=username, password=password, x_paths=x_paths)

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
            IDataBase.add_action_history(website_id=website.id, action_history=action_history)

    def add_task(self, website_id: int):
        print("adding task", website_id)
        website = IDataBase.get_website(website_id)
        self.scheduler.add_job(
            self._login_task,
            trigger=DateTrigger(run_date=website.next_schedule),
            args=[website_id],
            id=f"login_{website_id}",
            replace_existing=True,
            misfire_grace_time=3600
        )
        self.scheduler.print_jobs()



