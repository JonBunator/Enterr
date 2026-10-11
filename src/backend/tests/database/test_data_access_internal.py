from datetime import datetime

from dataAccess.data_access_internal import DataAccessInternal
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
        action_history=ActionHistory(
            execution_started=datetime(2024, 5, 10, 8, 0),
            execution_status=ActionStatusCode.IN_PROGRESS,
        ),
    )
    webhooks.reset_mock()

    data_access.action_history_finish_execution(
        action_history_id=action_history_id,
        execution_status=ActionStatusCode.FAILED,
        failed_details=ActionFailedDetails.UNKNOWN_EXECUTION_ERROR,
    )

    webhooks.action_history_changed.assert_called_once_with(
        action_history_id=action_history_id,
        website_id=website.id,
        user_id=user.id,
    )
