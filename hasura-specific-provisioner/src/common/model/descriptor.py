from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, validator

from src.common.model.constants import OPENMETADATA_SUPPORTED_DATATYPES


class DataProduct(BaseModel):
    id: str
    name: str
    domain: str
    environment: str
    version: str
    dataProductOwner: str
    devGroup: str
    ownerGroup: str
    specific: dict
    components: List[dict]


class OpenMetadataColumn(BaseModel):
    name: str
    dataType: str
    dataLength: Optional[int]
    precision: Optional[int]
    scale: Optional[int]

    @validator("dataType")
    def check_dataType(cls, value: str, values: dict) -> str:
        if value.upper() not in OPENMETADATA_SUPPORTED_DATATYPES:
            raise ValueError(
                'Column "'
                + values["name"]
                + '" specifies dataType of "'
                + value
                + '" but this is not a valid OpenMetadata data type'
            )
        return value


class DataContract(BaseModel):
    schema_: List[OpenMetadataColumn] = Field(..., alias="schema")


class Component(BaseModel):
    pass


class OutputPort(BaseModel):
    id: str
    name: str
    fullyQualifiedName: str
    description: str
    kind: Literal["outputport"]
    version: str
    infrastructureTemplateId: str
    useCaseTemplateId: str
    dependsOn: List[str]
    platform: str
    technology: str
    outputPortType: str
    creationDate: datetime
    startDate: datetime
    tags: List[str]
    sampleData: Any
    semanticLinking: List[Any]
    specific: Any


class HasuraOutputPortSpecific(BaseModel):
    customTableName: str
    select: str
    selectByPk: str
    selectAggregate: str
    selectStream: str


class HasuraOutputPort(OutputPort):
    platform: Literal["Hasura"]
    technology: Literal["Hasura"]
    outputPortType: Literal["GraphQL"]
    specific: HasuraOutputPortSpecific


class SnowflakeTable(BaseModel):
    database: str
    schema_: str = Field(..., alias="schema")
    table: str
