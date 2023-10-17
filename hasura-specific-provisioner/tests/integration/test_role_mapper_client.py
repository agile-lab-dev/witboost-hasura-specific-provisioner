import os
import pathlib
import time
from typing import Generator

import pytest
import requests
from httpx import Client
from requests.exceptions import ConnectionError
from testcontainers.core.container import DockerContainer  # type: ignore

from src.common.model.rolemapping import (
    GroupRoleMappings,
    Role,
    SystemError,
    UserRoleMappings,
    ValidationError,
)
from src.services.rolemapper import RoleMapperClient


class RoleMapperInDocker:
    container: DockerContainer
    rolemapper_url: str

    def __init__(self, container: DockerContainer, rolemapper_url: str):
        self.container = container
        self.rolemapper_url = rolemapper_url

    def wait_for_services(self, max_retries) -> None:
        health_url = self.rolemapper_url + "/v1/health"
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
            f"RoleMapperInDocker still not healthy after {max_retries} seconds."
        )


@pytest.fixture(scope="module")
def rolemapper_docker() -> Generator[RoleMapperInDocker, None, None]:
    open_api_host_path = str(
        pathlib.Path(__file__)
        .with_name("rolemapper-openapi-specification.yml")
        .resolve()
    )
    container = (
        DockerContainer(image="stoplight/prism:5.4.0")
        .with_volume_mapping(
            host=open_api_host_path, container="/tmp/openapi-specification.yml"
        )
        .with_bind_ports(container=4010, host=4010)
        .with_command(command="mock -h 0.0.0.0 /tmp/openapi-specification.yml")
    )
    with container:
        rolemapper_in_docker = RoleMapperInDocker(
            container, _get_rolemapper_url(container)
        )
        try:
            rolemapper_in_docker.wait_for_services(60)
        except Exception as e:
            stdout, stderr = container.get_logs()
            print("stdout:")
            print(stdout)
            print("stderr:")
            print(stderr)
            raise e
        yield rolemapper_in_docker


def _get_rolemapper_url(container: DockerContainer) -> str:
    # issue for win: https://github.com/testcontainers/testcontainers-python/issues/108#issuecomment-768367971
    host = "localhost" if os.name == "nt" else container.get_container_host_ip()
    rolemapper_url = "http://" + host + ":" + container.get_exposed_port(4010)
    return rolemapper_url


def test_create_role_success(rolemapper_docker: RoleMapperInDocker):
    client = RoleMapperClient(role_mapper_url=rolemapper_docker.rolemapper_url)
    to_be_created_role = Role(
        role_id="", component_id="", graphql_root_field_names=[""]
    )

    created_role = client.create_role(to_be_created_role)

    assert isinstance(created_role, Role)


def test_create_role_validation_error(rolemapper_docker: RoleMapperInDocker):
    http_client = Client(headers={"Prefer": "code=400"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    to_be_created_role = Role(
        role_id="", component_id="", graphql_root_field_names=[""]
    )

    error = client.create_role(to_be_created_role)

    assert isinstance(error, ValidationError)


def test_create_role_system_error(rolemapper_docker: RoleMapperInDocker):
    http_client = Client(headers={"Prefer": "code=500"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    to_be_created_role = Role(
        role_id="", component_id="", graphql_root_field_names=[""]
    )

    error = client.create_role(to_be_created_role)

    assert isinstance(error, SystemError)


def test_update_user_role_mappings_success(rolemapper_docker: RoleMapperInDocker):
    client = RoleMapperClient(role_mapper_url=rolemapper_docker.rolemapper_url)
    user_role_mapping_to_update = UserRoleMappings(role_id="", users=[""])

    user_role_mapping_updated = client.update_user_role_mappings(
        user_role_mapping_to_update
    )

    assert isinstance(user_role_mapping_updated, UserRoleMappings)


def test_update_user_role_validation_error(rolemapper_docker: RoleMapperInDocker):
    http_client = Client(headers={"Prefer": "code=400"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    user_role_mapping_to_update = UserRoleMappings(role_id="", users=[""])

    error = client.update_user_role_mappings(user_role_mapping_to_update)

    assert isinstance(error, ValidationError)


def test_update_user_role_system_error(rolemapper_docker: RoleMapperInDocker):
    http_client = Client(headers={"Prefer": "code=500"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    user_role_mapping_to_update = UserRoleMappings(role_id="", users=[""])

    error = client.update_user_role_mappings(user_role_mapping_to_update)

    assert isinstance(error, SystemError)


def test_update_group_role_mappings_success(rolemapper_docker: RoleMapperInDocker):
    client = RoleMapperClient(role_mapper_url=rolemapper_docker.rolemapper_url)
    group_role_mapping_to_update = GroupRoleMappings(role_id="", groups=[""])

    group_role_mapping_updated = client.update_group_role_mappings(
        group_role_mapping_to_update
    )

    assert isinstance(group_role_mapping_updated, GroupRoleMappings)


def test_update_group_role_mappings_validation_error(
    rolemapper_docker: RoleMapperInDocker,
):
    http_client = Client(headers={"Prefer": "code=400"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    group_role_mapping_to_update = GroupRoleMappings(role_id="", groups=[""])

    error = client.update_group_role_mappings(group_role_mapping_to_update)

    assert isinstance(error, ValidationError)


def test_update_group_role_mappings_system_error(rolemapper_docker: RoleMapperInDocker):
    http_client = Client(headers={"Prefer": "code=500"})
    client = RoleMapperClient(
        role_mapper_url=rolemapper_docker.rolemapper_url, client=http_client
    )
    group_role_mapping_to_update = GroupRoleMappings(role_id="", groups=[""])

    error = client.update_group_role_mappings(group_role_mapping_to_update)

    assert isinstance(error, SystemError)
