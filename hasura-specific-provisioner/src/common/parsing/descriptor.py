from typing import List, Tuple

import yaml

from src.common.model.descriptor import DataProduct, HasuraOutputPort, OutputPort


def parse_yaml_component_descriptor(
    descriptor_yaml: str,
) -> Tuple[DataProduct, HasuraOutputPort, OutputPort]:
    descriptor_dict = yaml.safe_load(descriptor_yaml)

    dataproduct_dict = descriptor_dict["dataProduct"]
    hasura_op_component_id = descriptor_dict["componentIdToProvision"]

    data_product = DataProduct.parse_obj(dataproduct_dict)

    hasura_op_dict = _find_component_by_component_id(
        data_product.components, hasura_op_component_id
    )
    hasura_op = HasuraOutputPort.parse_obj(hasura_op_dict)

    num_dependencies = len(hasura_op.dependsOn)
    if not num_dependencies == 1:
        raise ValueError(
            "Hasura Output Port dependency list should contain exactly one dependency,"
            " but instead had " + str(num_dependencies)
        )

    source_op_component_id = hasura_op.dependsOn[0]
    source_op_dict = _find_component_by_component_id(
        data_product.components, source_op_component_id
    )
    source_op = OutputPort.parse_obj(source_op_dict)

    return data_product, hasura_op, source_op


def _find_component_by_component_id(components: List[dict], id: str) -> dict:
    maybe_dict = next(
        (component for component in components if component["id"] == id), None
    )
    if maybe_dict is None:
        raise ValueError(
            "Unable to find component id " + id + " in Data Product components list"
        )
    else:
        return maybe_dict
