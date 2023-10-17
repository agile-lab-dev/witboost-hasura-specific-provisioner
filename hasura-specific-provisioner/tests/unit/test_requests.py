from .test_descriptors import descriptor_yaml_ok

provision_request: dict = {
    "descriptorKind": "COMPONENT_DESCRIPTOR",
    "descriptor": descriptor_yaml_ok,
}


bad_provision_request: dict = {
    "descriptorKind": "DATAPRODUCT_DESCRIPTOR",
    "descriptor": descriptor_yaml_ok,
}

update_acl_request: dict = {
    "refs": ["user1", "group2"],
    "provisionInfo": {"request": descriptor_yaml_ok, "result": ""},
}

validation_request: dict = {"descriptor": ""}
