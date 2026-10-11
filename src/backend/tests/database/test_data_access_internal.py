from datetime import datetime

from dataAccess.data_access_internal import DataAccessInternal
from dataAccess.database.change_database import DataBase
from dataAccess.database.database import (
    ActionHistory,
    ActionStatusCode,
    ActionFailedDetails,
)


def test_add_action_history_notifies_website_owner(
    session, webhooks, make_website, other_user
):
    website = make_website(owner=other_user)
    data_access = DataAccessInternal(webhook_endpoints=webhooks)

    action_history_id = data_access.add_action_history(
        website_id=website.id,
        user_id=website.user,
        action_history=ActionHistory(
            execution_started=datetime(2024, 5, 10, 8, 0),
            execution_status=ActionStatusCode.IN_PROGRESS,
        ),
    )

    webhooks.action_history_changed.assert_called_once_with(
        action_history_id=action_history_id,
        website_id=website.id,
        user_id=other_user.id,
    )


def test_finish_execution_notifies_website_owner(session, webhooks, make_website, user):
    website = make_website()
    data_access = DataAccessInternal(webhook_endpoints=webhooks)
    action_history_id = data_access.add_action_history(
        website_id=website.id,
        user_id=website.user,
        action_history=ActionHistory(
            execution_started=datetime(2024, 5, 10, 8, 0),
            execution_status=ActionStatusCode.IN_PROGRESS,
        ),
    )
    webhooks.reset_mock()

    data_access.action_history_finish_execution(
        action_history_id=action_history_id,
        user_id=website.user,
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.UNKNOWN_EXECUTION_ERROR,
    )

    webhooks.action_history_changed.assert_called_once_with(
        action_history_id=action_history_id,
        website_id=website.id,
        user_id=user.id,
    )


def test_unexpected_execution_failure_notifies_website_owner(
    session, webhooks, make_website, other_user, mocker
):
    website = make_website(owner=other_user)
    data_access = DataAccessInternal(webhook_endpoints=webhooks)
    for _ in range(2):
        session.add(
            ActionHistory(
                website=website.id,
                execution_started=datetime(2024, 5, 10, 8, 0),
                execution_status=ActionStatusCode.IN_PROGRESS,
            )
        )
    session.commit()
    get_owner = mocker.spy(DataBase, "get_website_owner_id")

    data_access.unexpected_execution_failure(
        website_id=website.id, execution_started=datetime(2024, 5, 10, 8, 0)
    )

    get_owner.assert_called_once_with(website.id)
    assert webhooks.action_history_changed.call_count == 2
    for call in webhooks.action_history_changed.call_args_list:
        assert call.kwargs["website_id"] == website.id
        assert call.kwargs["user_id"] == other_user.id
