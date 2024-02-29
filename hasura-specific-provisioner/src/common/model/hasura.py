from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel


class DataSourceType(StrEnum):
    SNOWFLAKE = "snowflake"
    POSTGRESQL = "pg"


class QualifiedTable(BaseModel):
    schema_name: str
    table_name: str


class TableConfig(BaseModel):
    data_source_type: DataSourceType
    data_source_name: str
    source_table: QualifiedTable
    custom_table_name: str
    select_root_field_name: str
    select_by_pk_root_field_name: str
    select_aggregate_root_field_name: str
    select_stream_root_field_name: str
    comment: str


class TrackTableResult(StrEnum):
    SUCCESS = auto()
    ALREADY_TRACKED = auto()
    FAILURE = auto()


class UntrackTableResult(StrEnum):
    SUCCESS = auto()
    NOT_TRACKED = auto()
    FAILURE = auto()


class CreateSelectPermissionResult(StrEnum):
    SUCCESS = auto()
    ALREADY_EXISTS = auto()
    FAILURE = auto()


class DropSelectPermissionResult(StrEnum):
    SUCCESS = auto()
    NOT_EXISTS = auto()
    FAILURE = auto()


class AddSourceResult(StrEnum):
    SUCCESS = auto()
    ALREADY_EXISTS = auto()
    FAILURE = auto()


class DropSourceResult(StrEnum):
    SUCCESS = auto()
    NOT_EXISTS = auto()
    FAILURE = auto()


class DataSourceConfig(BaseModel):
    data_source_type: DataSourceType
    data_source_name: str
    config: dict[str, Any]


class Health(StrEnum):
    OK = auto()
    METADATA_ERROR = auto()
    ERROR = auto()
