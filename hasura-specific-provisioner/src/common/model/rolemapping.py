from typing import List

from pydantic import BaseModel, Field


class Role(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    component_id: str = Field(
        ..., description="Component id in Witboost", example="urn:dmb:cmp:dom1:dp1:0:op"
    )
    graphql_root_field_names: List[str] = Field(
        ...,
        description="Root field name list",
        example=["dom1_dp1_0_op1_select", "dom1_dp1_0_op1_aggregate"],
    )


class UserRoleMappings(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    users: List[str] = Field(
        ..., description="User list", example=["user:user1", "user:user2"]
    )


class GroupRoleMappings(BaseModel):
    role_id: str = Field(..., description="Role id", example="dom1.dp1.0.op.readrole")
    groups: List[str] = Field(
        ..., description="Group list", example=["group:group1", "group:group2"]
    )


class ValidationError(BaseModel):
    errors: List[str]


class SystemError(BaseModel):
    error: str
