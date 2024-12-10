from datetime import datetime
from typing import List
from database.database import Website, _db as db, ActionHistory
from endpoints.models.website_model import AddWebsite, EditWebsite

class IDataBase:

    @staticmethod
    def get_all_websites() -> List[Website]:
        return db.session.scalars(db.select(Website)).all()

    @staticmethod
    def get_website(website_id: int) -> Website:
        return db.session.get(Website, website_id)

    @staticmethod
    def add_website(request: AddWebsite):
        website = request.to_sql_model()
        website.next_schedule = datetime.now()
        db.session.add(website)
        db.session.commit()

    @staticmethod
    def edit_website(request: EditWebsite):
        edit_id = request.id
        existing_website = db.session.get(Website, edit_id)
        request.edit_existing_model(existing_website)
        db.session.commit()

    @staticmethod
    def add_action_history(website_id: int, action_history: ActionHistory):
        website = db.session.get(Website, website_id)
        website.action_histories.append(action_history)
        website.next_schedule = website.action_interval.get_random_action_datetime()
        db.session.commit()

    @staticmethod
    def get_action_history(website: Website) -> List[ActionHistory]:
        return website.action_histories