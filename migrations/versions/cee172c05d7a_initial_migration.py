"""initial_migration

Revision ID: cee172c05d7a
Revises: 
Create Date: 2018-08-28 18:19:39.389889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cee172c05d7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('batches_story_billing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('put_into_queue', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('time')
    )
    op.create_table('batches_story_peaks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('put_into_queue', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('time')
    )
    op.create_table('clusters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('cpu_price', sa.Float(), nullable=True),
    sa.Column('memory_price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('servers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('cpu_price', sa.Float(), nullable=True),
    sa.Column('memory_price', sa.Float(), nullable=True),
    sa.Column('cluster_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], name='clusters_fk'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('services_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='team_fk'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('instance', sa.String(), nullable=False),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.Column('services_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['servers.id'], name='servers_fk'),
    sa.ForeignKeyConstraint(['services_group_id'], ['services_groups.id'], name='services_group_fk'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title', 'instance', 'services_group_id', 'server_id', name='ut_2')
    )
    op.create_table('metrics_billing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('type', sa.Enum('system_cpu_percent', 'user_cpu_percent', 'vsize', name='billing_metric_types'), nullable=True),
    sa.Column('batch_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('services_group_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['batch_id'], ['batches_story_billing.id'], name='batch_story_billing_fk'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='projects_fk'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='service_fk'),
    sa.ForeignKeyConstraint(['services_group_id'], ['services_groups.id'], name='services_groups_fk'),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='teams_fk'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('batch_id', 'type', 'service_id', 'services_group_id', name='metric_billing_ut_1')
    )
    op.create_table('metrics_peaks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('type', sa.Enum('system_cpu_percent', 'user_cpu_percent', 'vsize', name='peaks_metric_types'), nullable=True),
    sa.Column('batch_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('services_group_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['batch_id'], ['batches_story_peaks.id'], name='batch_story_peaks_fk'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='projects_fk'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='service_fk'),
    sa.ForeignKeyConstraint(['services_group_id'], ['services_groups.id'], name='services_groups_fk'),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name='teams_fk'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('batch_id', 'type', 'service_id', 'services_group_id', name='metric_peaks_ut_1')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('metrics_peaks')
    op.drop_table('metrics_billing')
    op.drop_table('services')
    op.drop_table('services_groups')
    op.drop_table('servers')
    op.drop_table('teams')
    op.drop_table('projects')
    op.drop_table('clusters')
    op.drop_table('batches_story_peaks')
    op.drop_table('batches_story_billing')
    op.drop_table('admins')
    # ### end Alembic commands ###
