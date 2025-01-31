"""empty message

Revision ID: 3975dcff04c0
Revises: 
Create Date: 2024-12-01 20:49:18.433162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3975dcff04c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('module',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('module_code', sa.String(length=100), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('members', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('enrolment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=True),
    sa.Column('module_id', sa.String(length=100), nullable=True),
    sa.Column('creator', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['module_id'], ['module.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('message', sa.String(length=5000), nullable=True),
    sa.Column('sender', sa.String(length=100), nullable=True),
    sa.Column('module', sa.String(length=100), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('downvotes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['module'], ['module.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vote',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(length=100), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('vote_type', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vote')
    op.drop_table('message')
    op.drop_table('enrolment')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))

    op.drop_table('user')
    op.drop_table('module')
    # ### end Alembic commands ###
