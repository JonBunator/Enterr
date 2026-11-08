from datetime import datetime, timezone
from typing import List, Annotated
from fastapi_pagination import Page
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import joinedload, selectinload, Session, aliased
from fastapi import Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_filters.ext.sqlalchemy import apply_sorting

from dataAccess.database.database import (
    Website,
    User,
    ActionHistory,
    ActionFailedDetails,
    ActionStatusCode,
    Notification,
    get_db_session,
    db_session,
)
from endpoints.models.action_history_model import GetActionHistory
from endpoints.models.notification_model import GetNotification
from endpoints.models.website_model import GetWebsite, WebsiteStatus
from utils.cookie_authentication import OAuth2PasswordBearerWithCookie
from utils.exceptions import NotFoundException
from utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/user/login")


class DataBase:
    """--------------------------- USER ACCESS ---------------------------"""

    @staticmethod
    def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        username = decode_token(token)
        if username is None:
            raise credentials_exception
        with get_db_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise credentials_exception
            return user

    @staticmethod
    def _join_latest_action(query, action_alias):
        """Outer join each website to its most recent action history."""
        latest_action_subquery = (
            select(
                ActionHistory.website,
                func.max(ActionHistory.execution_started).label(
                    "max_execution_started"
                ),
            )
            .group_by(ActionHistory.website)
            .subquery()
        )
        return query.outerjoin(
            latest_action_subquery,
            Website.id == latest_action_subquery.c.website,
        ).outerjoin(
            action_alias,
            and_(
                action_alias.website == Website.id,
                action_alias.execution_started
                == latest_action_subquery.c.max_execution_started,
            ),
        )

    @staticmethod
    def _website_status(action_alias):
        """Effective website status."""
        return case(
            (Website.paused == True, WebsiteStatus.PAUSED.value),
            (action_alias.id == None, WebsiteStatus.NO_LOGIN.value),
            (
                action_alias.execution_status == ActionStatusCode.IN_PROGRESS,
                WebsiteStatus.IN_PROGRESS.value,
            ),
            (
                action_alias.execution_status == ActionStatusCode.SUCCESS,
                WebsiteStatus.SUCCESS.value,
            ),
            else_=WebsiteStatus.FAILED.value,
        )

    @staticmethod
    def _filter_search(query, search):
        if not search:
            return query
        return query.where(
            Website.name.icontains(search, autoescape=True)
            | Website.url.icontains(search, autoescape=True)
        )

    @staticmethod
    def get_websites(
        current_user: User,
        search=None,
        sorting=None,
        website_status: WebsiteStatus = None,
    ) -> Page[GetWebsite]:
        """Get websites for the current user with optional filtering."""
        session = db_session.get()

        latest_success_subquery = (
            select(
                ActionHistory.website,
                func.max(ActionHistory.execution_started).label(
                    "max_success_started"
                ),
            )
            .where(ActionHistory.execution_status == ActionStatusCode.SUCCESS)
            .group_by(ActionHistory.website)
            .subquery()
        )

        action_alias = aliased(ActionHistory)
        success_alias = aliased(ActionHistory)

        last_login_col = action_alias.execution_started.label("last_login_attempt")

        last_success_ended_col = success_alias.execution_ended.label(
            "last_success_ended"
        )

        status_expr = DataBase._website_status(action_alias)
        status_col = status_expr.label("status")

        query = select(
            Website, last_login_col, status_col, last_success_ended_col
        ).where(Website.user == current_user.id)
        query = DataBase._join_latest_action(query, action_alias)
        query = (
            query.outerjoin(
                latest_success_subquery,
                Website.id == latest_success_subquery.c.website,
            )
            .outerjoin(
                success_alias,
                and_(
                    success_alias.website == Website.id,
                    success_alias.execution_started
                    == latest_success_subquery.c.max_success_started,
                ),
            )
            .options(joinedload(Website.action_interval))
        )

        query = DataBase._filter_search(query, search)

        if website_status == WebsiteStatus.FAILED:
            # Websites without any login are shown as failed
            query = query.where(
                status_expr.in_(
                    [WebsiteStatus.FAILED.value, WebsiteStatus.NO_LOGIN.value]
                )
            )
        elif website_status:
            query = query.where(status_expr == website_status.value)

        if sorting:
            status_sort_col = case(
                {
                    WebsiteStatus.IN_PROGRESS.value: 1,
                    WebsiteStatus.FAILED.value: 2,
                    WebsiteStatus.NO_LOGIN.value: 2,
                    WebsiteStatus.PAUSED.value: 3,
                    WebsiteStatus.SUCCESS.value: 4,
                },
                value=status_expr,
            )
            expiration_sort_col = func.julianday(last_success_ended_col) + (
                func.julianday(Website.expiration_interval)
                - func.julianday("1970-01-01")
            )
            query = apply_sorting(
                query,
                sorting,
                additional={
                    "last_login_attempt": last_login_col,
                    "status": status_sort_col,
                    "expiration": expiration_sort_col,
                },
            )

        # Tie-breaker so rows with equal sort values (e.g. NULL) page consistently
        query = query.order_by(Website.id)

        return paginate(
            session,
            query,
            transformer=lambda items: [
                GetWebsite.from_sql_model(item[0], item[1], item[2], item[3])
                for item in items
            ],
        )

    @staticmethod
    def get_website_status_counts(current_user: User, search=None) -> dict[str, int]:
        """Number of websites per status for the current user."""
        session = db_session.get()
        action_alias = aliased(ActionHistory)
        status_expr = DataBase._website_status(action_alias)

        query = (
            select(status_expr, func.count(Website.id))
            .select_from(Website)
            .where(Website.user == current_user.id)
        )
        query = DataBase._join_latest_action(query, action_alias)
        query = DataBase._filter_search(query, search).group_by(status_expr)

        counts = {
            website_status.value.lower(): 0
            for website_status in WebsiteStatus
            if website_status != WebsiteStatus.NO_LOGIN
        }
        for website_status, count in session.execute(query).all():
            if website_status == WebsiteStatus.NO_LOGIN.value:
                website_status = WebsiteStatus.FAILED.value
            counts[website_status.lower()] += count
        return counts

    @staticmethod
    def get_website(website_id: int, current_user: User) -> Website:
        session = db_session.get()
        query = session.query(Website).filter_by(id=website_id, user=current_user.id)
        query = query.options(joinedload(Website.action_interval))
        website = query.first()

        if website:
            return website
        raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def add_website(website: Website, current_user: User) -> Website:
        session = db_session.get()
        website.user = current_user.id
        if not website.paused:
            website.next_schedule = datetime.now(timezone.utc)
        session.add(website)
        session.commit()
        session.refresh(website)
        _ = website.action_interval
        return website

    @staticmethod
    def edit_website(website: Website, current_user: User):
        session = db_session.get()
        existing_website = (
            session.query(Website)
            .filter_by(id=website.id, user=current_user.id)
            .first()
        )
        if existing_website:
            session.merge(website)
            session.commit()
        else:
            raise NotFoundException(f"Website {website.id} not found")

    @staticmethod
    def delete_website(website_id: int, current_user: User):
        session = db_session.get()
        existing_website = (
            session.query(Website)
            .filter_by(id=website_id, user=current_user.id)
            .first()
        )
        if existing_website:
            session.delete(existing_website)
            session.commit()
        else:
            raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def trigger_login(website_id: int, current_user: User):
        session = db_session.get()
        website = (
            session.query(Website)
            .filter_by(id=website_id, user=current_user.id)
            .first()
        )
        if website:
            website.next_schedule = datetime.now(timezone.utc)
            session.commit()
        else:
            raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def get_action_histories(
        website_id: int, current_user: User
    ) -> Page[GetActionHistory]:
        session = db_session.get()
        website = session.get(Website, website_id)
        if website is None or website.user != current_user.id:
            raise NotFoundException(f"Website {website_id} not found")

        query = (
            select(ActionHistory)
            .where(ActionHistory.website == website_id)
            .order_by(ActionHistory.execution_started.desc())
        )

        return paginate(
            session,
            query,
            transformer=lambda items: [
                GetActionHistory.from_sql_model(item) for item in items
            ],
        )

    @staticmethod
    def get_action_history(action_history_id: int, current_user: User) -> ActionHistory:
        session = db_session.get()
        action_history = (
            session.query(ActionHistory)
            .join(Website, ActionHistory.website == Website.id)
            .filter(
                ActionHistory.id == action_history_id,
                Website.user == current_user.id,
            )
            .first()
        )
        if action_history:
            return action_history
        raise NotFoundException(f"ActionHistory {action_history_id} not found")

    @staticmethod
    def get_last_successful_login(
        website_id: int, current_user: User
    ) -> ActionHistory | None:
        session = db_session.get()
        website = session.get(Website, website_id)
        if website is None or website.user != current_user.id:
            raise NotFoundException(f"Website {website_id} not found")

        action_history = (
            session.query(ActionHistory)
            .filter_by(website=website_id, execution_status=ActionStatusCode.SUCCESS)
            .order_by(ActionHistory.execution_started.desc())
            .first()
        )

        return action_history

    @staticmethod
    def add_manual_action_history(
        website_id: int, action_history: ActionHistory, current_user: User
    ) -> ActionHistory:
        session = db_session.get()
        website = session.get(Website, website_id)
        if website is None or website.user != current_user.id:
            raise NotFoundException("Website not found")
        else:
            return DataBase.add_action_history(website_id, action_history, session)

    @staticmethod
    def add_notification(
        notification: Notification, current_user: User
    ) -> Notification:
        session = db_session.get()
        notification.user = current_user.id
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification

    @staticmethod
    def get_notification(notification_id: int, current_user: User) -> Notification:
        session = db_session.get()
        notification = (
            session.query(Notification)
            .filter_by(id=notification_id, user=current_user.id)
            .first()
        )
        if notification:
            return notification
        raise NotFoundException(f"Notification {notification_id} not found")

    @staticmethod
    def edit_notification(notification: Notification, current_user: User):
        session = db_session.get()
        existing_notification = (
            session.query(Notification)
            .filter_by(id=notification.id, user=current_user.id)
            .first()
        )
        if existing_notification:
            session.merge(notification)
            session.commit()
        else:
            raise NotFoundException(f"Notification {notification.id} not found")

    @staticmethod
    def delete_notification(notification: Notification, current_user: User):
        session = db_session.get()
        existing_notification = (
            session.query(Notification)
            .filter_by(id=notification.id, user=current_user.id)
            .first()
        )
        if existing_notification:
            session.delete(existing_notification)
            session.commit()
        else:
            raise NotFoundException(f"Notification {notification.id} not found")

    @staticmethod
    def get_notifications(current_user: User) -> Page[GetNotification]:
        session = db_session.get()
        query = select(Notification).where(Notification.user == current_user.id)

        return paginate(
            session,
            query,
            transformer=lambda items: [
                GetNotification.from_sql_model(item) for item in items
            ],
        )

    """--------------------------- INTERNAL ACCESS ---------------------------"""

    @staticmethod
    def get_user(username: str) -> User:
        with get_db_session() as session:
            return session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_website_by_id(website_id: int) -> Website:
        with get_db_session() as session:
            website = session.query(Website).filter_by(id=website_id).first()
            if website:
                return website
            raise NotFoundException(f"Website {website_id} not found")

    @staticmethod
    def get_notifications_all_users() -> List[Notification]:
        with get_db_session() as session:
            return session.query(Notification).all()

    @staticmethod
    def get_notifications_for_user(action_history: ActionHistory) -> List[Notification]:
        with get_db_session() as session:
            user_id = (
                session.query(Website).filter_by(id=action_history.website).first().user
            )
            return (
                session.query(Notification)
                .filter_by(user=user_id)
                .filter(
                    Notification._triggers.like(
                        f"%{action_history.execution_status.value}%"
                    )
                )
                .all()
            )

    @staticmethod
    def get_websites_all_users() -> List[Website]:
        with get_db_session() as session:
            stmt = select(Website).options(
                selectinload(Website.action_interval),
            )
            return session.scalars(stmt).all()

    @staticmethod
    def get_website_all_users(website_id: int) -> Website:
        with get_db_session() as session:
            website = (
                session.query(Website)
                .options(
                    joinedload(Website.action_interval),
                )
                .filter_by(id=website_id)
                .first()
            )

            if not website:
                raise NotFoundException(f"Website {website_id} not found")

            return website

    @staticmethod
    def action_history_finish_execution(
        action_history_id: int,
        execution_status: ActionStatusCode,
        failed_details: ActionFailedDetails,
        custom_failed_details_message: str = None,
        screenshot_id: str = None,
    ):
        with get_db_session() as session:
            existing_action_history = session.get(ActionHistory, action_history_id)
            if existing_action_history is None:
                return None
            existing_action_history.execution_ended = datetime.now(timezone.utc)
            existing_action_history.execution_status = execution_status
            existing_action_history.failed_details = failed_details
            existing_action_history.custom_failed_details_message = (
                custom_failed_details_message
            )
            existing_action_history.screenshot_id = screenshot_id
            website_id = existing_action_history.website
            session.commit()
            return website_id

    @staticmethod
    def set_next_schedule(website_id: int):
        with get_db_session() as session:
            website = (
                session.query(Website)
                .options(joinedload(Website.action_interval))
                .filter_by(id=website_id)
                .first()
            )
            if website is None:
                raise NotFoundException(f"Website {website_id} not found")

            if website.paused:
                website.next_schedule = None
            else:
                website.next_schedule = (
                    website.action_interval.get_random_action_datetime()
                )

            session.commit()

    @staticmethod
    def unexpected_execution_failure(
        website_id: int, execution_started: datetime
    ) -> List[int]:
        with get_db_session() as session:
            running_action_histories = (
                session.query(ActionHistory)
                .filter(
                    ActionHistory.execution_status == ActionStatusCode.IN_PROGRESS,
                    ActionHistory.website == website_id,
                )
                .all()
            )
            action_history_ids = []
            for action_history in running_action_histories:
                action_history.execution_status = ActionStatusCode.FAILED
                action_history.execution_ended = datetime.now(timezone.utc)
                action_history.failed_details = (
                    ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
                )
                action_history_ids.append(action_history.id)
            if len(running_action_histories) == 0:
                created_action_history = DataBase.add_action_history(
                    website_id,
                    ActionHistory(
                        execution_status=ActionStatusCode.FAILED,
                        execution_started=execution_started,
                        execution_ended=datetime.now(timezone.utc),
                        failed_details=ActionFailedDetails.UNKNOWN_EXECUTION_ERROR,
                    ),
                )
                action_history_ids.append(created_action_history.id)
            session.commit()
            return action_history_ids

    @staticmethod
    def add_action_history(
        website_id: int, action_history: ActionHistory, session: Session = None
    ) -> ActionHistory:
        def _add_action_history(session: Session) -> ActionHistory:
            website = session.get(Website, website_id)
            website.action_histories.append(action_history)
            session.commit()
            session.refresh(action_history)
            return action_history

        if session is not None:
            return _add_action_history(session)
        else:
            with get_db_session() as session:
                return _add_action_history(session)
