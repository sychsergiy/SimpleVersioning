import pytest

from griphook.server import db
from griphook.server import create_app
from griphook.server.models import (
    ServicesGroup,
    MetricPeak,
    MetricBilling,
    Project,
    Cluster,
    Server,
    Team,
)


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object("griphook.server.config.TestingConfig")
    return app


@pytest.fixture
def db_session(app):
    session = db.session
    db.drop_all()
    db.create_all()
    session.commit()
    yield session


@pytest.fixture
def create_project_team_test_data(db_session):
    db_session.add_all(
        [
            Project(id=1, title="test_project_1"),
            Project(id=2, title="test_project_2"),
            Project(id=3, title="test_project_3"),
        ]
    )
    db_session.commit()
    db_session.add_all(
        [
            Team(id=1, title="test_team_1"),
            Team(id=2, title="test_team_2"),
            Team(id=3, title="test_team_3"),
        ]
    )
    db_session.commit()
    db_session.add_all(
        [
            ServicesGroup(id=1, title="test_services_group_1"),
            ServicesGroup(id=2, title="test_services_group_2"),
            ServicesGroup(id=3, title="test_services_group_3"),
            ServicesGroup(id=4, title="test_services_group_4", project_id=2),
        ]
    )
    db_session.commit()
    db_session.add_all(
        [
            MetricPeak(id=1, value=152411, services_group_id=1),
            MetricPeak(id=2, value=159787, services_group_id=2),
            MetricPeak(id=3, value=156446, services_group_id=2),
            MetricPeak(id=4, value=132468, services_group_id=2),
            MetricPeak(id=5, value=798754, services_group_id=4, project_id=2),
            MetricPeak(id=6, value=798631, services_group_id=4, project_id=2),
            MetricPeak(id=7, value=798464, services_group_id=4, project_id=2),
        ]
    )
    db_session.commit()
    db_session.add_all(
        [
            MetricBilling(id=1, value=152411, services_group_id=1),
            MetricBilling(id=2, value=159787, services_group_id=2),
            MetricBilling(id=3, value=156446, services_group_id=2),
            MetricBilling(id=4, value=132468, services_group_id=2),
            MetricBilling(
                id=5, value=798754, services_group_id=4, project_id=2
            ),
            MetricBilling(
                id=6, value=798631, services_group_id=4, project_id=2
            ),
            MetricBilling(
                id=7, value=798464, services_group_id=4, project_id=2
            ),
        ]
    )
    db_session.commit()


@pytest.fixture
def create_server_cluster_test_data(db_session):
    db_session.add_all(
        [
            Server(id=1, title="test_server_1", cpu_price=2.4, memory_price=6),
            Server(id=2, title="test_server_2"),
        ]
    )
    db_session.add_all(
        [
            Cluster(id=1, title="test_cluster_1", cpu_price=3, memory_price=2),
            Cluster(id=2, title="test_cluster_2"),
        ]
    )
    db_session.commit()