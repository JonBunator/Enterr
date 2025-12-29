"""v3_0_0

Revision ID: ec08ca6514ef
Revises: db2df5c80c91
Create Date: 2025-12-27 10:24:54.359654

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec08ca6514ef"
down_revision: Union[str, None] = "db2df5c80c91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns first
    op.add_column(
        "action_history",
        sa.Column("custom_failed_details_message", sa.String(), nullable=True),
    )
    op.add_column(
        "website",
        sa.Column("custom_login_script", sa.String(), nullable=True),
    )

    # Migrate data from custom_access to custom_login_script
    connection = op.get_bind()

    result = connection.execute(
        sa.text(
            """
            SELECT website, username_xpath, password_xpath, submit_button_xpath
            FROM custom_access
            """
        )
    )

    for row in result:
        website_id, username_xpath, password_xpath, submit_button_xpath = row

        # Replace double quotes with single quotes to prevent breaking the generated script
        def sanitize_xpath(xpath):
            return xpath.replace('"', "'") if xpath else None

        username_xpath = sanitize_xpath(username_xpath)
        password_xpath = sanitize_xpath(password_xpath)
        submit_button_xpath = sanitize_xpath(submit_button_xpath)

        script_lines = []
        script_lines.append(
            f'fillUsername("{username_xpath}")'
            if username_xpath
            else "fillUsername()"
        )
        script_lines.append(
            f'fillPassword("{password_xpath}")'
            if password_xpath
            else "fillPassword()"
        )
        script_lines.append(
            f'clickSubmitButton("{submit_button_xpath}")'
            if submit_button_xpath
            else "clickSubmitButton()"
        )

        custom_login_script = "\n".join(script_lines)

        connection.execute(
            sa.text(
                """
                UPDATE website
                SET custom_login_script = :script
                WHERE id = :website_id
                """
            ),
            {"script": custom_login_script, "website_id": website_id},
        )

    op.drop_table("custom_access")
    op.drop_column("website", "pin")


def downgrade() -> None:
    op.create_table(
        "custom_access",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username_xpath", sa.String(), nullable=True),
        sa.Column("password_xpath", sa.String(), nullable=True),
        sa.Column("pin_xpath", sa.String(), nullable=True),
        sa.Column("submit_button_xpath", sa.String(), nullable=True),
        sa.Column("website", sa.Integer(), sa.ForeignKey("website.id"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "website",
        sa.Column("pin", sa.String(), nullable=True),
    )

    op.drop_column("action_history", "custom_failed_details_message")
    op.drop_column("website", "custom_login_script")
