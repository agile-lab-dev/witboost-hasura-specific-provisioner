import os
from typing import Annotated, Tuple, Union

from fastapi import Depends

from src.common.model.config import (
    HasuraConfig,
    ProvisionerConfig,
    RoleMapperConfig,
    SnowflakeConfig,
)
from src.common.model.descriptor import DataProduct, HasuraOutputPort, OutputPort
from src.common.parsing.descriptor import parse_yaml_component_descriptor
from src.models import (
    DescriptorKind,
    ProvisioningRequest,
    UpdateAclRequest,
    ValidationError,
)
from src.services.hasura.client import HasuraAdminClient
from src.services.hasura.provisioner import HasuraProvisioner
from src.services.rolemapper import RoleMapperClient


async def unpack_provisioning_request(
    provisioning_request: ProvisioningRequest,
) -> Union[Tuple[DataProduct, HasuraOutputPort, OutputPort], ValidationError]:
    if not provisioning_request.descriptorKind == DescriptorKind.COMPONENT_DESCRIPTOR:
        error = (
            "Expecting a COMPONENT_DESCRIPTOR but got a "
            f"{provisioning_request.descriptorKind} instead; please check with the "
            f"platform team."
        )
        return ValidationError(errors=[error])

    try:
        return parse_yaml_component_descriptor(provisioning_request.descriptor)
    except Exception as ex:
        return ValidationError(errors=["Unable to parse the descriptor.", str(ex)])


UnpackedProvisioningRequestDep = Annotated[
    Union[Tuple[DataProduct, HasuraOutputPort, OutputPort], ValidationError],
    Depends(unpack_provisioning_request),
]


async def unpack_update_acl_request(
    update_acl_request: UpdateAclRequest,
) -> Union[
    Tuple[DataProduct, HasuraOutputPort, OutputPort, list[str]], ValidationError
]:
    try:
        (
            data_product,
            hasura_output_port,
            source_output_port,
        ) = parse_yaml_component_descriptor(update_acl_request.provisionInfo.request)
        return (
            data_product,
            hasura_output_port,
            source_output_port,
            update_acl_request.refs,
        )
    except Exception as ex:
        return ValidationError(errors=["Unable to parse the descriptor.", str(ex)])


UnpackedUpdateAclRequestDep = Annotated[
    Union[Tuple[DataProduct, HasuraOutputPort, OutputPort, list[str]], ValidationError],
    Depends(unpack_update_acl_request),
]


def get_hasura_config_from_env() -> HasuraConfig:
    return HasuraConfig(
        url=get_env("HASURA_URL"),
        admin_secret=get_env("HASURA_ADMIN_SECRET"),
        timeout=int(get_env("HASURA_TIMEOUT")),
    )


def get_hasura_admin_client(
    hasura_config: Annotated[HasuraConfig, Depends(get_hasura_config_from_env)]
) -> HasuraAdminClient:
    return HasuraAdminClient(
        hasura_url=hasura_config.url,
        hasura_admin_secret=hasura_config.admin_secret,
        hasura_timeout=hasura_config.timeout,
    )


def get_role_mapper_config_from_env() -> RoleMapperConfig:
    return RoleMapperConfig(
        url=get_env("ROLE_MAPPER_URL"), timeout=int(get_env("ROLE_MAPPER_TIMEOUT"))
    )


def get_role_mapper_client(
    role_mapper_config: Annotated[
        RoleMapperConfig, Depends(get_role_mapper_config_from_env)
    ]
) -> RoleMapperClient:
    return RoleMapperClient(
        role_mapper_url=role_mapper_config.url,
        role_mapper_timeout=role_mapper_config.timeout,
    )


def get_provisioner_config_from_env() -> ProvisionerConfig:
    return ProvisionerConfig(
        snowflake_config=SnowflakeConfig(
            host=get_env("SNOWFLAKE_HOST"),
            user=get_env("SNOWFLAKE_USER"),
            password=get_env("SNOWFLAKE_PASSWORD"),
            role=get_env("SNOWFLAKE_ROLE"),
            warehouse=get_env("SNOWFLAKE_WAREHOUSE"),
        )
    )


def get_env(name: str) -> str:
    value = os.getenv(name)
    if value is not None:
        return value
    else:
        raise ValueError(f"Required environment variable {name} not found.")


def get_provisioner(
    hasura_admin_client: Annotated[HasuraAdminClient, Depends(get_hasura_admin_client)],
    role_mapper_client: Annotated[RoleMapperClient, Depends(get_role_mapper_client)],
    provisioner_config: Annotated[
        ProvisionerConfig, Depends(get_provisioner_config_from_env)
    ],
) -> HasuraProvisioner:
    provisioner = HasuraProvisioner(
        hasura_admin_client,
        role_mapper_client,
        provisioner_config,
    )
    return provisioner


HasuraProvisionerDep = Annotated[HasuraProvisioner, Depends(get_provisioner)]
