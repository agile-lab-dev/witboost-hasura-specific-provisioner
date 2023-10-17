from pydantic import BaseModel


class HasuraConfig(BaseModel):
    url: str
    admin_secret: str
    timeout: int


class RoleMapperConfig(BaseModel):
    url: str
    timeout: int


class SnowflakeConfig(BaseModel):
    host: str
    user: str
    password: str
    role: str
    warehouse: str


class ProvisionerConfig(BaseModel):
    snowflake_config: SnowflakeConfig
