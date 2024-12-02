from typing import List
from database.database import Website, _db as db, ActionHistory
from endpoints.models.website_model import AddWebsite, EditWebsite
from datetime import datetime

class IDataBase:

    @staticmethod
    def get_all_websites() -> List[Website]:
        return Website.query.all()

    @staticmethod
    def add_website(request: AddWebsite):
        website = request.to_sql_model()
        db.session.add(website)
        db.session.commit()

    @staticmethod
    def edit_website(request: EditWebsite):
        edit_id = request.id
        existing_website = Website.query.get(edit_id)
        request.edit_existing_model(existing_website)
        db.session.commit()

    @staticmethod
    def schedule_website_login(website: Website, dt: datetime):
        website.next_schedule = dt
        db.session.commit()

    @staticmethod
    def add_action_history(website_id: int, action_history: ActionHistory):
        website = Website.query.get(website_id)
        website.action_histories.append(action_history)
        website.next_schedule = website.action_interval.get_random_action_datetime()
        db.session.commit()

    @staticmethod
    def get_action_history(website: Website) -> List[ActionHistory]:
        return website.action_histories