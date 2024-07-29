"""initial settings

Revision ID: d3b37eefc4c3
Revises:
Create Date: 2024-07-14 23:06:51.269677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d3b37eefc4c3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create 'users' table first
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("nickname", sa.String(length=120), nullable=True),
        sa.Column("role", sa.Enum("user", "admin", name="userrole"), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("mobile", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Create 'conversations' table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_id"), "conversations", ["id"], unique=False)

    # Create 'drawing_diary' table
    op.create_table(
        "drawing_diary",
        sa.Column("drawing_diary_id", sa.Uuid(), nullable=False),
        sa.Column("image_url", sa.String(length=256), nullable=False),
        sa.Column("image_title", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("drawing_diary_id"),
    )
    op.create_index(
        op.f("ix_drawing_diary_drawing_diary_id"),
        "drawing_diary",
        ["drawing_diary_id"],
        unique=False,
    )

    # Create 'report_summary' table
    op.create_table(
        "report_summary",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contents", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_report_summary_id"), "report_summary", ["id"], unique=False
    )

    # Create 'emotion' table without 'report_id' foreign key
    op.create_table(
        "emotion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("comfortable_score", sa.Integer(), nullable=False),
        sa.Column("happy_score", sa.Integer(), nullable=False),
        sa.Column("sad_score", sa.Integer(), nullable=False),
        sa.Column("fun_score", sa.Integer(), nullable=False),
        sa.Column("annoyed_score", sa.Integer(), nullable=False),
        sa.Column("lethargic_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emotion_id"), "emotion", ["id"], unique=False)

    # Create 'report' table, now with 'emotion_id' foreign key
    op.create_table(
        "report",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("drawing_diary_id", sa.Uuid(), nullable=False),
        sa.Column("emotion_id", sa.Uuid(), nullable=False),
        sa.Column("report_summary_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["drawing_diary_id"],
            ["drawing_diary.drawing_diary_id"],
        ),
        sa.ForeignKeyConstraint(
            ["emotion_id"],
            ["emotion.id"],
        ),
        sa.ForeignKeyConstraint(
            ["report_summary_id"],
            ["report_summary.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_report_id"), "report", ["id"], unique=False)

    # Update 'emotion' table to add 'report_id' foreign key
    op.add_column("emotion", sa.Column("report_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_emotion_report_id",
        "emotion",
        "report",
        ["report_id"],
        ["id"],
    )

    # Create 'messages' table
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("is_from_user", sa.Boolean(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("message_timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)

    # Create remaining tables
    op.create_table(
        "lemons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lemon_count", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_lemons_id"), "lemons", ["id"], unique=False)

    op.create_table(
        "tags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("report_summary_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["report_summary_id"],
            ["report_summary.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)

    op.create_table(
        "images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("path", sa.String(length=256), nullable=False),
        sa.Column("extension", sa.String(length=8), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("message_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["messages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_table("images")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_lemons_id"), table_name="lemons")
    op.drop_table("lemons")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_report_id"), table_name="report")
    op.drop_index(op.f("ix_report_summary_id"), table_name="report_summary")
    op.drop_table("report")
    op.drop_index(op.f("ix_conversations_id"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_index(op.f("ix_drawing_diary_drawing_diary_id"), table_name="drawing_diary")
    op.drop_table("drawing_diary")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
