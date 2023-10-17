from src.common.parsing.descriptor import parse_yaml_component_descriptor
from tests.unit.test_descriptors import (
    data_product_ok,
    descriptor_yaml_ok,
    hasura_op_ok,
    snowflake_op_ok,
)


def test_parse_yaml_descriptor() -> None:
    data_product, hasura_op, snowflake_op = parse_yaml_component_descriptor(
        descriptor_yaml_ok
    )

    assert data_product == data_product_ok
    assert hasura_op == hasura_op_ok
    assert snowflake_op == snowflake_op_ok
