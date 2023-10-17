import os
import pathlib
import time
from typing import Generator
from urllib.parse import urlparse

import pytest
import requests
from _pytest.fixtures import FixtureRequest
from requests.exceptions import ConnectionError
from testcontainers.compose import DockerCompose  # type: ignore

from src.common.model.hasura import (
    AddSourceResult,
    CreateSelectPermissionResult,
    DataSourceConfig,
    DataSourceType,
    DropSelectPermissionResult,
    DropSourceResult,
    Health,
    QualifiedTable,
    TableConfig,
    TrackTableResult,
    UntrackTableResult,
)
from src.services.hasura.client import HasuraAdminClient


class HasuraInDocker:
    compose: DockerCompose
    hasura_url: str
    hasura_admin_secret: str

    def __init__(
        self, compose: DockerCompose, hasura_url: str, hasura_admin_secret: str
    ):
        self.compose = compose
        self.hasura_url = hasura_url
        self.hasura_admin_secret = hasura_admin_secret

    def wait_for_services(self, max_retries) -> None:
        health_url = self.hasura_url + "/healthz?strict=false"
        retries = max_retries
        while retries >= 0:
            try:
                response = requests.get(health_url)
                if response.status_code == 200:
                    return None
            except ConnectionError:
                pass
            time.sleep(1)
            retries -= 1
        raise Exception(
            f"HasuraInDocker still not healthy after {max_retries} seconds."
        )


@pytest.fixture(scope="module")
def hasura_docker() -> Generator[HasuraInDocker, None, None]:
    compose = DockerCompose(
        filepath=str(pathlib.Path(__file__).parent.resolve()),
        compose_file_name="hasura-ee-snowflake-docker-compose.yaml",
        pull=True,
    )
    with compose:
        hasura_admin_secret = compose.exec_in_container(
            "hasura", ["bash", "-c", "echo -n $HASURA_GRAPHQL_ADMIN_SECRET"]
        )[0]

        hasura_url = _get_hasura_url(compose)

        hasura_in_docker = HasuraInDocker(compose, hasura_url, hasura_admin_secret)
        try:
            hasura_in_docker.wait_for_services(60)
        except Exception as e:
            stdout, stderr = compose.get_logs()
            print("stdout:")
            print(stdout)
            print("stderr:")
            print(stderr)
            raise e
        yield hasura_in_docker
        # Teardown code is not necessary, as the Docker environment
        # will be automatically shut down when exiting the context manager


def _get_hasura_url(compose: DockerCompose) -> str:
    # look for DOCKER_HOST
    docker_host = os.environ.get("DOCKER_HOST")

    # determine Hasura host based on DOCKER_HOST's status
    # - if it is not set, we're in a normal setting (eg, local) and can use
    #   DockerCompose's methods to retrieve the service host
    # - if it is set, we're most likely using DIND (eg, CI/CD), and should use that
    #   host instead
    hasura_host = (
        "localhost"
        # issue for win: https://github.com/testcontainers/testcontainers-python/issues/108#issuecomment-768367971
        if os.name == "nt"
        else compose.get_service_host("hasura", 8080)
        if docker_host is None
        else urlparse(docker_host).hostname
    )

    hasura_url = (
        "http://" + hasura_host + ":" + compose.get_service_port("hasura", 8080)
    )

    return hasura_url


@pytest.fixture
def schema_name(request: FixtureRequest, hasura_docker: HasuraInDocker):
    schema_name = "schema_" + request.node.name
    yield schema_name
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )
    statements = ["DROP SCHEMA IF EXISTS " + schema_name + " CASCADE"]
    client.run_sql(statements=statements, cascade=True)
    client.clear_metadata("I know this will clear Hasura metadata irrecoverably")


def test_create_client(hasura_docker: HasuraInDocker):
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )
    health = client.health_check()
    assert health == Health.OK


def test_run_sql(hasura_docker: HasuraInDocker, schema_name: str) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE test_table(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    response = client.run_sql(statements)

    assert response.status_code == 200


def test_get_source_tables(schema_name: str, hasura_docker: HasuraInDocker) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE test_table_2(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    run_sql_response = client.run_sql(statements)

    assert run_sql_response.status_code == 200

    tables = client.get_source_tables()

    assert any(
        table.table_name == "test_table_2" and table.schema_name == schema_name
        for table in tables
    )


def test_track_table(schema_name: str, hasura_docker: HasuraInDocker) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    table_name = "test_table_track"
    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE " + table_name + "(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    run_sql_response = client.run_sql(statements)
    assert run_sql_response.status_code == 200

    table_config: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(schema_name=schema_name, table_name=table_name),
        custom_table_name=table_name,
        select_root_field_name=table_name + "_select",
        select_by_pk_root_field_name=table_name + "_select_one",
        select_aggregate_root_field_name=table_name + "_aggregate",
        select_stream_root_field_name=table_name + "_stream",
        comment="Access to the " + table_name + " table in schema " + schema_name,
    )

    # should succeed
    res1 = client.track_table(table_config)
    assert res1 == TrackTableResult.SUCCESS

    # should fail (already tracked)
    res2 = client.track_table(table_config)
    assert res2 == TrackTableResult.ALREADY_TRACKED

    # should fail (already tracked, even though the fields have changed)
    table_config2: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(schema_name=schema_name, table_name=table_name),
        custom_table_name=table_name,
        select_root_field_name=table_name + "_select_renamed",
        select_by_pk_root_field_name=table_name + "_select_one_renamed",
        select_aggregate_root_field_name=table_name + "_aggregate_renamed",
        select_stream_root_field_name=table_name + "_stream",
        comment="GraphQL Output Port to get data from the "
        + table_name
        + " table in schema "
        + schema_name,
    )
    res3 = client.track_table(table_config2)
    assert res3 == TrackTableResult.ALREADY_TRACKED


def test_untrack_table(schema_name: str, hasura_docker: HasuraInDocker) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    table_name = "test_table_untrack"
    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE " + table_name + "(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    run_sql_response = client.run_sql(statements)
    assert run_sql_response.status_code == 200

    table_config: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(schema_name=schema_name, table_name=table_name),
        custom_table_name=table_name,
        select_root_field_name=table_name + "_select",
        select_by_pk_root_field_name=table_name + "_select_one",
        select_aggregate_root_field_name=table_name + "_aggregate",
        select_stream_root_field_name=table_name + "_stream",
        comment="Access to the " + table_name + " table in schema " + schema_name,
    )

    # should succeed
    res1 = client.track_table(table_config)
    assert res1 == TrackTableResult.SUCCESS

    # should succeed
    res2 = client.untrack_table(table_config)
    assert res2 == UntrackTableResult.SUCCESS

    # should fail (already untracked)
    res3 = client.untrack_table(table_config)
    assert res3 == UntrackTableResult.NOT_TRACKED

    # should fail (never tracked it, and it does not exist)
    table_config2: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(
            schema_name=schema_name, table_name=table_name + "_non_existent"
        ),
        custom_table_name=table_name + "_non_existent",
        select_root_field_name=table_name + "_select_renamed",
        select_by_pk_root_field_name=table_name + "_select_one_renamed",
        select_aggregate_root_field_name=table_name + "_aggregate_renamed",
        select_stream_root_field_name=table_name + "_stream_renamed",
        comment="GraphQL Output Port to get data from the "
        + table_name
        + " table in schema "
        + schema_name,
    )
    res3 = client.untrack_table(table_config2)
    assert res3 == UntrackTableResult.NOT_TRACKED


def test_create_select_permission(
    schema_name: str, hasura_docker: HasuraInDocker
) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    table_name = "test_table_create_permission"
    role_id = "role_test_table_create_permission"

    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE " + table_name + "(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    run_sql_response = client.run_sql(statements)
    assert run_sql_response.status_code == 200

    table_config: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(schema_name=schema_name, table_name=table_name),
        custom_table_name=table_name,
        select_root_field_name=table_name + "_select",
        select_by_pk_root_field_name=table_name + "_select_one",
        select_aggregate_root_field_name=table_name + "_aggregate",
        select_stream_root_field_name=table_name + "_stream",
        comment="Access to the " + table_name + " table in schema " + schema_name,
    )

    # should succeed
    res1 = client.track_table(table_config)
    assert res1 == TrackTableResult.SUCCESS

    # should succeed
    res2 = client.create_select_permission(table_config, role_id)
    assert res2 == CreateSelectPermissionResult.SUCCESS

    # should fail (already exists)
    res3 = client.create_select_permission(table_config, role_id)
    assert res3 == CreateSelectPermissionResult.ALREADY_EXISTS


def test_drop_select_permission(
    schema_name: str, hasura_docker: HasuraInDocker
) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    table_name = "test_table_drop_permission"
    role_id = "role_test_table_drop_permission"

    statements = [
        "CREATE SCHEMA " + schema_name,
        "SET SEARCH_PATH = " + schema_name,
        "CREATE TABLE " + table_name + "(col1 VARCHAR PRIMARY KEY, col2 VARCHAR)",
    ]
    run_sql_response = client.run_sql(statements)
    assert run_sql_response.status_code == 200

    table_config: TableConfig = TableConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="default",
        source_table=QualifiedTable(schema_name=schema_name, table_name=table_name),
        custom_table_name=table_name,
        select_root_field_name=table_name + "_select",
        select_by_pk_root_field_name=table_name + "_select_one",
        select_aggregate_root_field_name=table_name + "_aggregate",
        select_stream_root_field_name=table_name + "_stream",
        comment="Access to the " + table_name + " table in schema " + schema_name,
    )

    # should succeed
    res1 = client.track_table(table_config)
    assert res1 == TrackTableResult.SUCCESS

    # should fail (not exists)
    res2 = client.drop_select_permission(table_config, role_id)
    assert res2 == DropSelectPermissionResult.NOT_EXISTS

    # should succeed
    res3 = client.create_select_permission(table_config, role_id)
    assert res3 == CreateSelectPermissionResult.SUCCESS

    # should succeed
    res4 = client.drop_select_permission(table_config, role_id)
    assert res4 == DropSelectPermissionResult.SUCCESS

    # should fail (not exists)
    res5 = client.drop_select_permission(table_config, role_id)
    assert res5 == DropSelectPermissionResult.NOT_EXISTS


def test_clear_metadata(hasura_docker) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    with pytest.raises(ValueError):
        client.clear_metadata("Wrong")

    response = client.clear_metadata(
        "I know this will clear Hasura metadata irrecoverably"
    )

    assert response.status_code == 200


def test_add_drop_source(hasura_docker: HasuraInDocker) -> None:
    client = HasuraAdminClient(
        hasura_url=hasura_docker.hasura_url,
        hasura_admin_secret=hasura_docker.hasura_admin_secret,
    )

    pg_config = {
        "connection_info": {
            "database_url": {
                "connection_parameters": {
                    "username": "postgres",
                    "password": "postgrespassword",
                    "database": "postgres",
                    "host": "postgres",
                    "port": 5432,
                }
            }
        }
    }

    data_source_config = DataSourceConfig(
        data_source_type=DataSourceType.POSTGRESQL,
        data_source_name="test_add_drop_source",
        config=pg_config,
    )

    # should fail (not exists)
    res1 = client.drop_source(data_source_config)
    assert res1 == DropSourceResult.NOT_EXISTS

    # should succeed
    res2 = client.add_source(data_source_config)
    assert res2 == AddSourceResult.SUCCESS

    # should fail (already exists)
    res3 = client.add_source(data_source_config)
    assert res3 == AddSourceResult.ALREADY_EXISTS

    # should succeed
    res4 = client.drop_source(data_source_config)
    assert res4 == DropSourceResult.SUCCESS

    # should fail (not exists)
    res5 = client.drop_source(data_source_config)
    assert res5 == DropSourceResult.NOT_EXISTS
