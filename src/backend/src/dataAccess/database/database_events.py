from sqlalchemy.event import listens_for
from sqlalchemy.orm.attributes import get_history

from dataAccess.database.database import Website, ActionHistory
from execution.scheduler import Scheduler
from sqlalchemy.orm import object_session

def register_database_events(scheduler: Scheduler):
    @listens_for(Website, "after_insert")
    def _website_added(_mapper, _connection, target):
        session = object_session(target)
        if session:
            @listens_for(session, "after_commit")
            def after_commit(_session):
                scheduler.add_task(target.id)

    @listens_for(Website, "after_update")
    def _website_paused_changed(_mapper, _connection, target):
        history = get_history(target, "paused")
        if history.has_changes():
            session = object_session(target)
            if session:
                @listens_for(session, "after_commit")
                def after_commit(_session):
                    if target.paused:
                        scheduler.remove_task(target.id)
                    else:
                        scheduler.add_task(target.id)

    @listens_for(Website, "after_update")
    def _website_next_schedule_changed(_mapper, _connection, target):
        history = get_history(target, "next_schedule")
        if history.has_changes():
            session = object_session(target)
            if session:
                @listens_for(session, "after_commit")
                def after_commit(_session):
                    if not target.paused:
                        scheduler.add_task(target.id)

    @listens_for(Website, "after_delete")
    def _website_deleted(_mapper, _connection, target):
        session = object_session(target)
        if session:
            @listens_for(session, "after_commit")
            def after_commit(_session):
                scheduler.remove_task(target.id)

    @listens_for(ActionHistory, "after_insert")
    def _action_history_added(_mapper, _connection, target):
        session = object_session(target)
        if session:
            @listens_for(session, "after_commit")
            def after_commit(_session):
                scheduler.add_task(target.website)
