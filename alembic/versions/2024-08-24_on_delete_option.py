"""on delete option

Revision ID: d0d9ed663f47
Revises: 8901d415592d
Create Date: 2024-08-24 10:43:00.165433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d0d9ed663f47"
down_revision: Union[str, None] = "8901d415592d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("images_conversation_id_fkey", "images", type_="foreignkey")
    op.drop_constraint("images_message_id_fkey", "images", type_="foreignkey")
    op.create_foreign_key(
        None, "images", "conversations", ["conversation_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "images", "messages", ["message_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("messages_conversation_id_fkey", "messages", type_="foreignkey")
    op.create_foreign_key(
        None,
        "messages",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("report_drawing_diary_id_fkey", "report", type_="foreignkey")
    op.drop_constraint("report_conversation_id_fkey", "report", type_="foreignkey")
    op.drop_constraint("report_emotion_id_fkey", "report", type_="foreignkey")
    op.drop_constraint("report_report_summary_id_fkey", "report", type_="foreignkey")
    op.create_foreign_key(
        None, "report", "conversations", ["conversation_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "report", "emotion", ["emotion_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None,
        "report",
        "report_summary",
        ["report_summary_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "report",
        "drawing_diary",
        ["drawing_diary_id"],
        ["drawing_diary_id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("tags_report_summary_id_fkey", "tags", type_="foreignkey")
    op.create_foreign_key(
        None,
        "tags",
        "report_summary",
        ["report_summary_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "tags", type_="foreignkey")
    op.create_foreign_key(
        "tags_report_summary_id_fkey",
        "tags",
        "report_summary",
        ["report_summary_id"],
        ["id"],
    )
    op.drop_constraint(None, "report", type_="foreignkey")
    op.drop_constraint(None, "report", type_="foreignkey")
    op.drop_constraint(None, "report", type_="foreignkey")
    op.drop_constraint(None, "report", type_="foreignkey")
    op.create_foreign_key(
        "report_report_summary_id_fkey",
        "report",
        "report_summary",
        ["report_summary_id"],
        ["id"],
    )
    op.create_foreign_key(
        "report_emotion_id_fkey", "report", "emotion", ["emotion_id"], ["id"]
    )
    op.create_foreign_key(
        "report_conversation_id_fkey",
        "report",
        "conversations",
        ["conversation_id"],
        ["id"],
    )
    op.create_foreign_key(
        "report_drawing_diary_id_fkey",
        "report",
        "drawing_diary",
        ["drawing_diary_id"],
        ["drawing_diary_id"],
    )
    op.drop_constraint(None, "messages", type_="foreignkey")
    op.create_foreign_key(
        "messages_conversation_id_fkey",
        "messages",
        "conversations",
        ["conversation_id"],
        ["id"],
    )
    op.drop_constraint(None, "images", type_="foreignkey")
    op.drop_constraint(None, "images", type_="foreignkey")
    op.create_foreign_key(
        "images_message_id_fkey", "images", "messages", ["message_id"], ["id"]
    )
    op.create_foreign_key(
        "images_conversation_id_fkey",
        "images",
        "conversations",
        ["conversation_id"],
        ["id"],
    )
    # ### end Alembic commands ###
