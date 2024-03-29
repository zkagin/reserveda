"""add owner to items

Revision ID: 57666459c2b6
Revises: 5ba037608d10
Create Date: 2020-10-08 14:51:12.577722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "57666459c2b6"
down_revision = "5ba037608d10"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("item", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "item", "user", ["owner_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "item", type_="foreignkey")
    op.drop_column("item", "owner_id")
    # ### end Alembic commands ###
