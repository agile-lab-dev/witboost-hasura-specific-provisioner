from typing import List, Union
from urllib.parse import quote

from src.common.model.config import ProvisionerConfig
from src.common.model.descriptor import DataProduct, HasuraOutputPort, OutputPort
from src.common.model.hasura import (
    AddSourceResult,
    CreateSelectPermissionResult,
    DataSourceConfig,
    DataSourceType,
    QualifiedTable,
    TableConfig,
    TrackTableResult,
    UntrackTableResult,
)
from src.common.model.rolemapping import GroupRoleMappings, Role, UserRoleMappings
from src.models import (
    ProvisioningStatus,
    Status1,
    ValidationError,
    ValidationResult,
)
from src.services.hasura.client import HasuraAdminClient
from src.services.rolemapper import RoleMapperClient


# TODO logging
class HasuraProvisioner(object):
    def __init__(
        self,
        hasura_admin_client: HasuraAdminClient,
        role_mapper_client: RoleMapperClient,
        provisioner_config: ProvisionerConfig,
    ):
        self._hasura_admin_client = hasura_admin_client
        self._role_mapper_client = role_mapper_client
        self._config = provisioner_config

    def validate(
        self,
        data_product: DataProduct,
        hasura_output_port: HasuraOutputPort,
        source_output_port: OutputPort,
    ) -> ValidationResult:
        prefix = _make_prefix(data_product, hasura_output_port)

        hop_specific = hasura_output_port.specific
        customTableName = hop_specific.customTableName
        select = hop_specific.select
        selectByPk = hop_specific.selectByPk
        selectAggregate = hop_specific.selectAggregate
        selectStream = hop_specific.selectStream

        errors: list[str] = []

        # check prefixes
        if not customTableName.startswith(prefix):
            errors.append(
                _make_prefix_error(
                    customTableName, "customTableName", "custom table name", prefix
                )
            )
        if not select.startswith(prefix):
            errors.append(
                _make_prefix_error(select, "select", "select root field", prefix)
            )
        if not selectByPk.startswith(prefix):
            errors.append(
                _make_prefix_error(
                    selectByPk, "selectByPk", "select by primary key root field", prefix
                )
            )
        if not selectAggregate.startswith(prefix):
            errors.append(
                _make_prefix_error(
                    selectAggregate,
                    "selectAggregate",
                    "select aggregate root field",
                    prefix,
                )
            )
        if not selectStream.startswith(prefix):
            errors.append(
                _make_prefix_error(
                    selectStream, "selectStream", "select stream root field", prefix
                )
            )

        # check root fields are unique
        root_fields_set = {select, selectByPk, selectAggregate, selectStream}
        if len(root_fields_set) < 4:
            errors.append(
                "The provided root field names are not unique. Check "
                "fields: select, selectByPk, selectAggregate and "
                "selectStream and verify they are unique."
            )

        if len(errors) == 0:
            return ValidationResult(valid=True)
        else:
            return ValidationResult(valid=False, error=ValidationError(errors=errors))

    def provision(
        self,
        data_product: DataProduct,
        hasura_output_port: HasuraOutputPort,
        source_output_port: OutputPort,
    ) -> Union[ProvisioningStatus, ValidationError]:
        validation_result = self.validate(
            data_product, hasura_output_port, source_output_port
        )

        if not validation_result.valid:
            return validation_result.error  # type: ignore[return-value]

        data_source_config, table_config = self._make_data_source_and_table_configs(
            data_product, hasura_output_port, source_output_port
        )

        add_source_res = self._hasura_admin_client.add_source(data_source_config)

        if (
            add_source_res == AddSourceResult.SUCCESS
            or add_source_res == AddSourceResult.ALREADY_EXISTS
        ):
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result="Unable to add data source; please check with the platform team.",  # noqa E501
            )

        track_table_res = self._hasura_admin_client.track_table(table_config)

        if (
            track_table_res == TrackTableResult.SUCCESS
            or track_table_res == TrackTableResult.ALREADY_TRACKED
        ):
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result="Unable to track table; please check with the platform team.",
            )

        role_id = _make_role_id(data_product, hasura_output_port)
        role = Role(
            role_id=role_id,
            component_id=hasura_output_port.id,
            graphql_root_field_names=[
                table_config.select_root_field_name,
                table_config.select_by_pk_root_field_name,
                table_config.select_aggregate_root_field_name,
                table_config.select_stream_root_field_name,
            ],
        )

        create_role_res = self._role_mapper_client.create_role(role)

        if type(create_role_res) == Role:
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result="Unable to create role; please check with the platform team.",
            )

        create_select_permission_res = (
            self._hasura_admin_client.create_select_permission(table_config, role_id)
        )

        if (
            create_select_permission_res == CreateSelectPermissionResult.SUCCESS
            or create_select_permission_res
            == CreateSelectPermissionResult.ALREADY_EXISTS
        ):
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result=(
                    "Unable to create permissions for table; "
                    "please check with the platform team."
                ),
            )

        # TODO deploy info
        # info = Info(publicInfo={"info": "link to hasura, example query"})
        info = None

        return ProvisioningStatus(
            status=Status1.COMPLETED, result="Provisioning completed", info=info
        )

    def unprovision(
        self,
        data_product: DataProduct,
        hasura_output_port: HasuraOutputPort,
        source_output_port: OutputPort,
    ) -> Union[ProvisioningStatus, ValidationError]:
        validation_result = self.validate(
            data_product, hasura_output_port, source_output_port
        )

        if not validation_result.valid:
            return validation_result.error  # type: ignore[return-value]

        data_source_config, table_config = self._make_data_source_and_table_configs(
            data_product, hasura_output_port, source_output_port
        )

        untrack_table_res = self._hasura_admin_client.untrack_table(table_config)

        if (
            untrack_table_res == UntrackTableResult.SUCCESS
            or untrack_table_res == UntrackTableResult.NOT_TRACKED
        ):
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result="Unable to untrack table; please check with the platform team.",
            )

        # TODO smart drop source
        # for now, do not drop source as it may be used by to other OPs
        # we need to check, for now leave it

        # TODO remove role and mappings
        #  (delete role + put empty role mappings for groups and users?)
        # for now we can leave them, they create no issues

        return ProvisioningStatus(
            status=Status1.COMPLETED, result="Unprovisioning completed"
        )

    def update_acl(
        self,
        data_product: DataProduct,
        hasura_output_port: HasuraOutputPort,
        source_output_port: OutputPort,
        refs: List[str],
    ) -> Union[ProvisioningStatus, ValidationError]:
        validation_result = self.validate(
            data_product, hasura_output_port, source_output_port
        )

        if not validation_result.valid:
            return validation_result.error  # type: ignore[return-value]

        role_id = _make_role_id(data_product, hasura_output_port)
        users = [user for user in refs if user.startswith("user:")]
        groups = [group for group in refs if group.startswith("group:")]
        user_role_mappings = UserRoleMappings(role_id=role_id, users=users)
        group_role_mappings = GroupRoleMappings(role_id=role_id, groups=groups)

        user_role_mapping_res = self._role_mapper_client.update_user_role_mappings(
            user_role_mappings
        )

        if type(user_role_mapping_res) == UserRoleMappings:
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result=(
                    "Unable to update user role mappings; "
                    "please check with the platform team."
                ),
            )

        group_role_mapping_res = self._role_mapper_client.update_group_role_mappings(
            group_role_mappings
        )

        if type(group_role_mapping_res) == GroupRoleMappings:
            pass
        else:
            return ProvisioningStatus(
                status=Status1.FAILED,
                result=(
                    "Unable to update group role mappings; "
                    "please check with the platform team."
                ),
            )

        return ProvisioningStatus(
            status=Status1.COMPLETED, result="Update ACL completed"
        )

    def _make_data_source_and_table_configs(
        self, data_product, hasura_output_port, source_output_port
    ):
        hop_specific = hasura_output_port.specific
        schema = source_output_port.specific["schema"].upper()
        table = source_output_port.specific["viewName"].upper()
        data_source_config = DataSourceConfig(
            data_source_type=DataSourceType.SNOWFLAKE,
            data_source_name=_make_source_name(data_product),
            config={
                "fully_qualify_all_names": False,
                "jdbc_url": self._make_snowflake_jdbc_url(source_output_port),
            },
        )
        table_config = TableConfig(
            data_source_type=DataSourceType.SNOWFLAKE.value,
            data_source_name=_make_source_name(data_product),
            source_table=QualifiedTable(
                schema_name=schema,
                table_name=table,
            ),
            custom_table_name=hop_specific.customTableName,
            select_root_field_name=hop_specific.select,
            select_by_pk_root_field_name=hop_specific.selectByPk,
            select_aggregate_root_field_name=hop_specific.selectAggregate,
            select_stream_root_field_name=hop_specific.selectStream,
            comment=f"Access to the {table} table in schema {schema}",
        )

        return data_source_config, table_config

    def _make_snowflake_jdbc_url(self, snowflake_output_port: OutputPort) -> str:
        sc = self._config.snowflake_config
        db = snowflake_output_port.specific["database"]
        schema = snowflake_output_port.specific["schema"]

        jdbc_url = (
            f"jdbc:snowflake://{sc.host}/?"
            f"user={sc.user}&password={quote(sc.password)}&"
            f"role={sc.role}&warehouse={sc.warehouse}&"
            f"db={db}&schema={schema}"
        )

        return jdbc_url


def _normalize(value: str) -> str:
    return value.replace(" ", "").replace("-", "").lower()


def _make_prefix(dp: DataProduct, op: HasuraOutputPort) -> str:
    domain_normalized = _normalize(dp.domain)
    dpname_normalized = _normalize(dp.name)
    dp_major_version = _normalize(dp.version.split(".")[0])
    opname_normalized = _normalize(op.name)
    prefix = f"{domain_normalized}_{dpname_normalized}_{dp_major_version}_{opname_normalized}_"  # noqa E501

    return prefix


def _make_prefix_error(value, field_name, field_friendly_name, prefix) -> str:
    error = (
        f"The {field_friendly_name} (field: {field_name}) must start with prefix "
        f'"{prefix}" but the actual value "{value}" does not.'
        f"The format of the prefix is "
        "<domain>_<data product name>_<data product major version>_<output port name> "
        "where all the components are normalized (only lowercase letters and numbers)."
    )
    return error


def _make_source_name(dp: DataProduct) -> str:
    domain_normalized = _normalize(dp.domain)
    dpname_normalized = _normalize(dp.name)
    dp_major_version = _normalize(dp.version.split(".")[0])
    return f"{domain_normalized}_{dpname_normalized}_{dp_major_version}"


def _make_role_id(dp: DataProduct, op: HasuraOutputPort) -> str:
    prefix = _make_prefix(dp, op)
    return f"{prefix}role"
