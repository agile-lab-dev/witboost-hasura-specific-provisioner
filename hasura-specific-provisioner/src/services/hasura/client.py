import codecs
import logging
from typing import List, Optional, Union

from httpx import Client, Response
from pydantic import parse_obj_as

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
from src.services.hasura.auth import HasuraAdminTokenAuth


class HasuraAdminClient(object):
    _metadata_endpoint: str
    _query_endpoint: str
    _health_endpoint: str
    _client: Client

    def __init__(
        self, hasura_url: str, hasura_admin_secret: str, hasura_timeout: int = 30
    ):
        self._metadata_endpoint = self._ensure_slash(hasura_url) + "v1/metadata"
        self._query_endpoint = self._ensure_slash(hasura_url) + "v2/query"
        self._health_endpoint = self._ensure_slash(hasura_url) + "healthz"
        auth = HasuraAdminTokenAuth(hasura_admin_secret)
        self._client = Client(auth=auth, timeout=hasura_timeout)
        self._logger = logging.getLogger(__name__)

    def add_source(self, data_source_config: DataSourceConfig) -> AddSourceResult:
        """
        Add a data source according to the provided config
        """

        self._logger.info(f"Attempting to add source with config: {data_source_config}")
        response = self._add_source(data_source_config)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return AddSourceResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                if code is not None and code == "already-exists":
                    return AddSourceResult.ALREADY_EXISTS
                else:
                    return AddSourceResult.FAILURE
            else:
                return AddSourceResult.FAILURE

    def drop_source(self, data_source_config: DataSourceConfig) -> DropSourceResult:
        """
        Drop a data source according to the provided config
        """

        self._logger.info(
            f"Attempting to drop source with config: {data_source_config}"
        )
        response = self._drop_source(data_source_config)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return DropSourceResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                if code is not None and code == "not-exists":
                    return DropSourceResult.NOT_EXISTS
                else:
                    return DropSourceResult.FAILURE
            else:
                return DropSourceResult.FAILURE

    def track_table(self, table_config: TableConfig) -> TrackTableResult:
        """
        Track a table according to the provided config
        """

        self._logger.info(f"Attempting to track table with config: {table_config}")
        response = self._track_table(table_config)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return TrackTableResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                if code is not None and code == "already-tracked":
                    return TrackTableResult.ALREADY_TRACKED
                else:
                    return TrackTableResult.FAILURE
            else:
                return TrackTableResult.FAILURE

    def untrack_table(self, table_config: TableConfig) -> UntrackTableResult:
        """
        Untrack a table according to the provided config
        """

        self._logger.info(f"Attempting to untrack table with config: {table_config}")
        response = self._untrack_table(table_config)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return UntrackTableResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                if code is not None and code == "already-untracked":
                    return UntrackTableResult.NOT_TRACKED
                else:
                    return UntrackTableResult.FAILURE
            else:
                return UntrackTableResult.FAILURE

    def create_select_permission(
        self, table_config: TableConfig, role_id: str
    ) -> CreateSelectPermissionResult:
        self._logger.info(
            "Attempting to create select permission on table with "
            + f"config: {table_config} for role: {role_id}"
        )
        response = self._create_select_permission(table_config, role_id)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return CreateSelectPermissionResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                if code is not None and code == "already-exists":
                    return CreateSelectPermissionResult.ALREADY_EXISTS
                else:
                    return CreateSelectPermissionResult.FAILURE
            else:
                return CreateSelectPermissionResult.FAILURE

    def drop_select_permission(
        self, table_config: TableConfig, role_id: str
    ) -> DropSelectPermissionResult:
        self._logger.info(
            "Attempting to drop select permission on table with "
            + f"config: {table_config} for role: {role_id}"
        )
        response = self._drop_select_permission(table_config, role_id)
        self._logger.info(f"Got response: {response}")

        if response.status_code == 200:
            return DropSelectPermissionResult.SUCCESS
        else:
            if response.status_code == 400:
                code = response.json()["code"]
                error = response.json()["error"]
                if (
                    code is not None
                    and code == "permission-denied"  # ???
                    and error is not None
                    and "does not exist" in error
                ):
                    return DropSelectPermissionResult.NOT_EXISTS
                else:
                    return DropSelectPermissionResult.FAILURE
            else:
                return DropSelectPermissionResult.FAILURE

    def get_source_tables(
        self, data_source_config: Optional[DataSourceConfig] = None
    ) -> list[QualifiedTable]:
        """
        Returns the list of tables in the source
        """

        target_data_source = (
            "default"
            if data_source_config is None
            else data_source_config.data_source_name
        )
        target_data_source_type = (
            "pg"
            if data_source_config is None
            else data_source_config.data_source_type.value
        )

        request_body = {
            "type": target_data_source_type + "_get_source_tables",
            "args": {"source": target_data_source},
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to get source tables: {request_body}"
        )
        response = self._client.post(self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        # rename "schema" field into "schema_name" and "table" field into "table_name"
        # to have an easier time with Pydantic
        def rename_fields(table_objects: List[dict]) -> List[dict]:
            key_mapping = {
                "schema": "schema_name",
                "name": "table_name",
            }
            new_table_objects = map(
                lambda table_object: {
                    key_mapping.get(k, k): v for k, v in table_object.items()
                },
                table_objects,
            )
            return list(new_table_objects)

        json = rename_fields(response.json())

        tables = parse_obj_as(list[QualifiedTable], json)

        return tables

    def run_sql(
        self,
        statements: List[str],
        data_source_config: Optional[DataSourceConfig] = None,
        cascade: bool = False,
        check_metadata_consistency: bool = False,
    ) -> Response:
        """
        Run the SQL statements against the specified source; if None specified, run
        the statements against the underlying PostgreSQL database
        """

        target_data_source = (
            "default"
            if data_source_config is None
            else data_source_config.data_source_name
        )
        target_data_source_type = (
            "pg"
            if data_source_config is None
            else data_source_config.data_source_type.value
        )

        def create_run_sql_args(statement: str) -> dict:
            return {
                "type": target_data_source_type + "_run_sql",
                "args": {
                    "source": target_data_source,
                    "sql": statement,
                    "cascade": cascade,
                    "check_metadata_consistency": check_metadata_consistency,
                },
            }

        queries = list(map(create_run_sql_args, statements))
        request_body = {"type": "bulk", "args": queries}

        self._logger.debug(
            f"Calling {self._query_endpoint} to run SQL queries: {request_body}"
        )
        response = self._client.post(self._query_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def health_check(self) -> Health:
        """
        Performs a health check on Hasura.
        """
        response = self._client.get(
            url=self._health_endpoint, params=[("strict", False)]
        )

        if response.status_code == 200:
            if "WARN" in response.text:
                return Health.METADATA_ERROR
            else:
                return Health.OK
        else:
            return Health.ERROR

    def clear_metadata(self, magic_word: str) -> Response:
        # Samuel L. Jackson would not be entertained
        magic_word_check = codecs.encode(
            "V xabj guvf jvyy pyrne Unfhen zrgnqngn veerpbirenoyl", "rot13"
        )
        if not magic_word == magic_word_check:
            raise ValueError("Ah ah ah! You didn't say the magic word!")

        request_body = {"type": "clear_metadata", "args": {}}

        self._logger.debug(f"Calling {self._metadata_endpoint} to clear metadata")
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _add_source(self, data_source_config: DataSourceConfig) -> Response:
        """
        Perform the REST request to create a data source according to the provided
        config
        """
        request_body = {
            "type": data_source_config.data_source_type.value + "_add_source",
            "args": {
                "name": data_source_config.data_source_name,
                "configuration": data_source_config.config,
            },
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to add source: {request_body}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _drop_source(
        self, data_source_config: DataSourceConfig, cascade: bool = False
    ) -> Response:
        """
        Perform the REST request to drop a data source according to the provided config
        """
        request_body = {
            "type": data_source_config.data_source_type.value + "_drop_source",
            "args": {"name": data_source_config.data_source_name, "cascade": cascade},
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to drop source: {request_body}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _track_table(self, table_config: TableConfig) -> Response:
        """
        Perform the REST request to track a table according to the provided config
        """
        request_body = {
            "type": table_config.data_source_type.value + "_track_table",
            "args": {
                "source": table_config.data_source_name,
                "table": self._make_table_spec(table_config),
                "configuration": {
                    "custom_name": table_config.custom_table_name,
                    "custom_root_fields": {
                        "select": table_config.select_root_field_name,
                        "select_by_pk": table_config.select_by_pk_root_field_name,
                        "select_aggregate": table_config.select_aggregate_root_field_name,  # noqa E501
                    },
                    "comment": table_config.comment,
                },
                "apollo_federation_config": {"enable": "v1"},
            },
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to track table: {request_body}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _untrack_table(
        self, table_config: TableConfig, cascade: bool = False
    ) -> Response:
        """
        Perform the REST request to untrack a table according to the provided config
        """
        request_body = {
            "type": table_config.data_source_type.value + "_untrack_table",
            "args": {
                "table": self._make_table_spec(table_config),
                "source": table_config.data_source_name,
                "cascade": cascade,
            },
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to untrack table: {request_body}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _create_select_permission(
        self, table_config: TableConfig, role_id: str
    ) -> Response:
        """
        Perform the REST request to add read permissions on a tracked table to the
        provided role
        """
        request_body = {
            "type": table_config.data_source_type.value + "_create_select_permission",
            "args": {
                "table": self._make_table_spec(table_config),
                "role": role_id,
                "permission": {
                    "columns": "*",
                    "filter": {},
                    "set": [],
                    "allow_aggregations": False,
                },
                "source": table_config.data_source_name,
            },
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to create read permissions on table:"
            + f" {request_body} to role {role_id}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _drop_select_permission(
        self, table_config: TableConfig, role_id: str
    ) -> Response:
        """
        Perform the REST request to remove read permissions on a tracked table from
        the provided role
        """

        request_body = {
            "type": table_config.data_source_type.value + "_drop_select_permission",
            "args": {
                "table": self._make_table_spec(table_config),
                "role": role_id,
                "source": table_config.data_source_name,
            },
        }

        self._logger.debug(
            f"Calling {self._metadata_endpoint} to drop read permissions on table: "
            + f"{request_body} to role {role_id}"
        )
        response = self._client.post(url=self._metadata_endpoint, json=request_body)
        self._logger.debug(f"Got response: {response.json()}")

        return response

    def _make_table_spec(self, table_config: TableConfig) -> Union[list[str], dict]:
        ds_type = table_config.data_source_type
        if ds_type == DataSourceType.POSTGRESQL:
            return {
                "schema": table_config.source_table.schema_name,
                "name": table_config.source_table.table_name,
            }
        if ds_type == DataSourceType.SNOWFLAKE:
            return [table_config.source_table.table_name]
        else:
            raise ValueError(f"Unsupported data source type {ds_type}")

    @staticmethod
    def _ensure_slash(url: str) -> str:
        if not url.endswith("/"):
            return url + "/"
        return url
