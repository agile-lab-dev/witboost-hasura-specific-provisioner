import logging
from typing import Optional, Union

from httpx import Client

from src.common.model.rolemapping import (
    GroupRoleMappings,
    Role,
    SystemError,
    UserRoleMappings,
    ValidationError,
)


class RoleMapperClient(object):
    _roles_endpoint: str
    _user_roles_endpoint: str
    _group_roles_endpoint: str
    _client: Client

    def __init__(
        self,
        role_mapper_url: str,
        role_mapper_timeout: int = 30,
        client: Optional[Client] = None,
    ):
        self._roles_endpoint = self._ensure_slash(role_mapper_url) + "v1/roles"
        self._user_roles_endpoint = (
            self._ensure_slash(role_mapper_url) + "v1/user_roles"
        )
        self._group_roles_endpoint = (
            self._ensure_slash(role_mapper_url) + "v1/group_roles"
        )
        self._health_endpoint = self._ensure_slash(role_mapper_url) + "v1/health"
        self._client = Client(timeout=role_mapper_timeout) if client is None else client
        self._logger = logging.getLogger(__name__)

    def create_role(self, role: Role) -> Union[Role, ValidationError, SystemError]:
        self._logger.debug(f"Calling {self._roles_endpoint} to create role: {role}")
        response = self._client.put(self._roles_endpoint, json=role.dict())
        self._logger.debug(f"Got response: {response.json()}")

        status_code = response.status_code
        if status_code == 200:
            return Role.parse_obj(response.json())
        if status_code == 400:
            return ValidationError.parse_obj(response.json())
        if status_code == 500:
            return SystemError.parse_obj(response.json())
        else:
            raise ValueError(f"Unknown response: {response}")

    def update_user_role_mappings(
        self, user_role_mappings: UserRoleMappings
    ) -> Union[UserRoleMappings, ValidationError, SystemError]:
        self._logger.debug(
            f"Calling {self._user_roles_endpoint} to update user role "
            f"mappings: {user_role_mappings}"
        )
        response = self._client.put(
            self._user_roles_endpoint, json=user_role_mappings.dict()
        )
        self._logger.debug(f"Got response: {response.json()}")

        status_code = response.status_code
        if status_code == 200:
            return UserRoleMappings.parse_obj(response.json())
        if status_code == 400:
            return ValidationError.parse_obj(response.json())
        if status_code == 500:
            return SystemError.parse_obj(response.json())
        else:
            raise ValueError(f"Unknown response: {response}")

    def update_group_role_mappings(
        self, group_role_mappings: GroupRoleMappings
    ) -> Union[GroupRoleMappings, ValidationError, SystemError]:
        self._logger.debug(
            f"Calling {self._group_roles_endpoint} to update group role "
            f"mappings: {group_role_mappings}"
        )
        response = self._client.put(
            self._group_roles_endpoint, json=group_role_mappings.dict()
        )
        self._logger.debug(f"Got response: {response.json()}")

        status_code = response.status_code
        if status_code == 200:
            return GroupRoleMappings.parse_obj(response.json())
        if status_code == 400:
            return ValidationError.parse_obj(response.json())
        if status_code == 500:
            return SystemError.parse_obj(response.json())
        else:
            raise ValueError(f"Unknown response: {response}")

    @staticmethod
    def _ensure_slash(url: str) -> str:
        if not url.endswith("/"):
            return url + "/"
        return url
