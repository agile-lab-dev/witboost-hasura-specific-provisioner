from unittest.mock import Mock

from src.common.model.config import ProvisionerConfig, SnowflakeConfig
from src.common.model.hasura import (
    AddSourceResult,
    CreateSelectPermissionResult,
    TrackTableResult,
    UntrackTableResult,
)
from src.common.model.rolemapping import (
    GroupRoleMappings,
    Role,
    UserRoleMappings,
)
from src.common.model.rolemapping import (
    ValidationError as RoleMappingValidationError,
)
from src.common.parsing.descriptor import parse_yaml_component_descriptor
from src.models import ProvisioningStatus, Status1, ValidationError
from src.services.hasura.provisioner import HasuraProvisioner
from tests.unit.test_descriptors import (
    descriptor_yaml_ok,
    descriptor_yaml_validation_ko,
)

provisioner_config = ProvisionerConfig(
    snowflake_config=SnowflakeConfig(
        host="", user="", password="", role="", warehouse=""
    )
)


def test_provisioner_validate_success() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=Mock(), provisioner_config=Mock(), role_mapper_client=Mock()
    )

    validation_result = provisioner.validate(data_product, hasura_op, snowflake_op)

    assert validation_result.valid


def test_provisioner_validate_fail() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_validation_ko
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=Mock(), provisioner_config=Mock(), role_mapper_client=Mock()
    )

    validation_result = provisioner.validate(data_product, hasura_op, snowflake_op)

    assert validation_result.valid is False
    assert isinstance(validation_result.error, ValidationError)
    assert len(validation_result.error.errors) == 6


def test_provisioner_provision_success() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.add_source.return_value = AddSourceResult.SUCCESS
    hasura_admin_client.track_table.return_value = TrackTableResult.SUCCESS
    hasura_admin_client.create_select_permission.return_value = (
        CreateSelectPermissionResult.SUCCESS
    )
    role_mapper_client = Mock()
    role_mapper_client.create_role.return_value = Role(
        role_id="", component_id="", graphql_root_field_names=[""]
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.provision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.COMPLETED


def test_provisioner_provision_failure_add_source() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.add_source.return_value = AddSourceResult.FAILURE
    role_mapper_client = Mock()
    provisioner_config = ProvisionerConfig(
        snowflake_config=SnowflakeConfig(
            host="", user="", password="", role="", warehouse=""
        )
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.provision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_provision_failure_track_table() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.add_source.return_value = AddSourceResult.SUCCESS
    hasura_admin_client.track_table.return_value = TrackTableResult.FAILURE
    role_mapper_client = Mock()
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.provision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_provision_failure_create_role() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.add_source.return_value = AddSourceResult.SUCCESS
    hasura_admin_client.track_table.return_value = TrackTableResult.SUCCESS
    role_mapper_client = Mock()
    role_mapper_client.create_role.return_value = RoleMappingValidationError(
        errors=[""]
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.provision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_provision_failure_select_permission() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.add_source.return_value = AddSourceResult.SUCCESS
    hasura_admin_client.track_table.return_value = TrackTableResult.SUCCESS
    hasura_admin_client.create_select_permission.return_value = (
        CreateSelectPermissionResult.FAILURE
    )
    role_mapper_client = Mock()
    role_mapper_client.create_role.return_value = Role(
        role_id="", component_id="", graphql_root_field_names=[""]
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.provision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_unprovision_success() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.untrack_table.return_value = UntrackTableResult.SUCCESS
    role_mapper_client = Mock()
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.unprovision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.COMPLETED


def test_provisioner_unprovision_failure_untrack_table() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    hasura_admin_client.untrack_table.return_value = UntrackTableResult.FAILURE
    role_mapper_client = Mock()
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.unprovision(data_product, hasura_op, snowflake_op)

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_update_acl_success() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    role_mapper_client = Mock()
    role_mapper_client.update_user_role_mappings.return_value = UserRoleMappings(
        role_id="", users=[""]
    )
    role_mapper_client.update_group_role_mappings.return_value = GroupRoleMappings(
        role_id="", groups=[""]
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.update_acl(
        data_product, hasura_op, snowflake_op, ["user"]
    )

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.COMPLETED


def test_provisioner_update_acl_failure_update_user_role_mappings() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    role_mapper_client = Mock()
    role_mapper_client.update_user_role_mappings.return_value = (
        RoleMappingValidationError(errors=[""])
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.update_acl(
        data_product, hasura_op, snowflake_op, ["user"]
    )

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED


def test_provisioner_update_acl_failure_update_group_role_mappings() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )
    hasura_admin_client = Mock()
    role_mapper_client = Mock()
    role_mapper_client.update_user_role_mappings.return_value = UserRoleMappings(
        role_id="", users=[""]
    )
    role_mapper_client.update_group_role_mappings.return_value = (
        RoleMappingValidationError(errors=[""])
    )
    provisioner = HasuraProvisioner(
        hasura_admin_client=hasura_admin_client,
        provisioner_config=provisioner_config,
        role_mapper_client=role_mapper_client,
    )

    provisioning_status = provisioner.update_acl(
        data_product, hasura_op, snowflake_op, ["user"]
    )

    assert isinstance(provisioning_status, ProvisioningStatus)
    assert provisioning_status.status == Status1.FAILED
