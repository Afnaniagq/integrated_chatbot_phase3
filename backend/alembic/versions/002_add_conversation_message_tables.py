"""Add Conversation and Message tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversation table
    op.create_table('conversation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create message table
    op.create_table('message',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('idx_conversation_created_at', 'conversation', ['created_at'])
    op.create_index('idx_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('idx_message_user_id', 'message', ['user_id'])
    op.create_index('idx_message_created_at', 'message', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_message_created_at', table_name='message')
    op.drop_index('idx_message_user_id', table_name='message')
    op.drop_index('idx_message_conversation_id', table_name='message')
    op.drop_index('idx_conversation_created_at', table_name='conversation')
    op.drop_index('idx_conversation_user_id', table_name='conversation')

    # Drop message table
    op.drop_table('message')

    # Drop conversation table
    op.drop_table('conversation')