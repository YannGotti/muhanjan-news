from alembic import op
import sqlalchemy as sa

revision = "20260421_0002"
down_revision = "20260421_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE submissions SET approved_at = created_at "
        "WHERE status = 'approved' AND approved_at IS NULL"
    )
    op.create_index(
        "uq_submissions_user_source_message",
        "submissions",
        ["user_id", "source_message_id"],
        unique=True,
        postgresql_where=sa.text("source_message_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_submissions_user_source_message", table_name="submissions")
