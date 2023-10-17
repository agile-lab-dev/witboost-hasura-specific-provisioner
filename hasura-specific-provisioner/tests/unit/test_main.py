from unittest.mock import Mock

from fastapi.testclient import TestClient

from src.dependencies import get_provisioner
from src.main import app
from src.models import ProvisioningStatus, Status1, ValidationError, ValidationResult

from .test_requests import (
    bad_provision_request,
    provision_request,
    update_acl_request,
    validation_request,
)

client = TestClient(app)


def test_main_provision_success() -> None:
    def mock_provisioner():
        m = Mock()
        m.provision.return_value = ProvisioningStatus(
            status=Status1.COMPLETED, result=""
        )
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/provision", json=provision_request)

    assert response.status_code == 200
    assert response.json() == {"info": None, "result": "", "status": "COMPLETED"}
    app.dependency_overrides = {}


def test_main_provision_failure_validation_error() -> None:
    def mock_provisioner():
        m = Mock()
        m.provision.return_value = ValidationError(errors=["error"])
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/provision", json=provision_request)

    assert response.status_code == 400
    assert response.json() == {"errors": ["error"]}
    app.dependency_overrides = {}


def test_main_provision_failure_validation_error_unpack() -> None:
    def mock_provisioner():
        m = Mock()
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/provision", json=bad_provision_request)

    assert response.status_code == 400
    assert response.json() == {
        "errors": [
            "Expecting a COMPONENT_DESCRIPTOR but got a "
            + "DescriptorKind.DATAPRODUCT_DESCRIPTOR instead; please check with "
            + "the platform team."
        ]
    }
    app.dependency_overrides = {}


def test_main_provision_status_not_implemented() -> None:
    response = client.get("/v1/provision/token/status")

    assert response.status_code == 500
    assert response.json() == {"error": "Not implemented"}


def test_main_unprovision_success() -> None:
    def mock_provisioner():
        m = Mock()
        m.unprovision.return_value = ProvisioningStatus(
            status=Status1.COMPLETED, result=""
        )
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/unprovision", json=provision_request)

    assert response.status_code == 200
    assert response.json() == {"info": None, "result": "", "status": "COMPLETED"}
    app.dependency_overrides = {}


def test_main_unprovision_failure_validation_error() -> None:
    def mock_provisioner():
        m = Mock()
        m.unprovision.return_value = ValidationError(errors=["error"])
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/unprovision", json=provision_request)

    assert response.status_code == 400
    assert response.json() == {"errors": ["error"]}
    app.dependency_overrides = {}


def test_main_unprovision_failure_validation_error_unpack() -> None:
    def mock_provisioner():
        return Mock()

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/unprovision", json=bad_provision_request)

    assert response.status_code == 400
    assert response.json() == {
        "errors": [
            "Expecting a COMPONENT_DESCRIPTOR but got a "
            + "DescriptorKind.DATAPRODUCT_DESCRIPTOR instead; please check with "
            + "the platform team."
        ]
    }
    app.dependency_overrides = {}


def test_main_update_acl_success() -> None:
    def mock_provisioner():
        m = Mock()
        m.update_acl.return_value = ProvisioningStatus(
            status=Status1.COMPLETED, result=""
        )
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/updateacl", json=update_acl_request)

    assert response.status_code == 200
    assert response.json() == {"info": None, "result": "", "status": "COMPLETED"}
    app.dependency_overrides = {}


def test_main_update_acl_failure_validation_error() -> None:
    def mock_provisioner():
        m = Mock()
        m.update_acl.return_value = ValidationError(errors=["error"])
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/updateacl", json=update_acl_request)

    assert response.status_code == 400
    assert response.json() == {"errors": ["error"]}
    app.dependency_overrides = {}


def test_main_validate_success() -> None:
    def mock_provisioner():
        m = Mock()
        m.validate.return_value = ValidationResult(valid=True)
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/validate", json=provision_request)

    assert response.status_code == 200
    assert response.json() == {"error": None, "valid": True}
    app.dependency_overrides = {}


def test_main_validate_failure_validation_error() -> None:
    def mock_provisioner():
        m = Mock()
        m.validate.return_value = ValidationResult(
            valid=False, error=ValidationError(errors=["error1"])
        )
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/validate", json=provision_request)

    assert response.status_code == 200
    assert response.json() == {"error": {"errors": ["error1"]}, "valid": False}
    app.dependency_overrides = {}


def test_main_validate_failure_validation_error_unpack() -> None:
    def mock_provisioner():
        return Mock()

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/validate", json=bad_provision_request)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "errors": [
                "Expecting a COMPONENT_DESCRIPTOR but got a "
                + "DescriptorKind.DATAPRODUCT_DESCRIPTOR instead; please "
                + "check with the platform team."
            ]
        },
        "valid": False,
    }
    app.dependency_overrides = {}


def test_main_v2_validate_not_implemented() -> None:
    response = client.post("/v2/validate", json=validation_request)

    assert response.status_code == 500
    assert response.json() == {"error": "Not implemented"}


def test_main_v2_validate_status_not_implemented() -> None:
    response = client.get("/v2/validate/token/status")

    assert response.status_code == 500
    assert response.json() == {"error": "Not implemented"}


def test_main_provision_exception() -> None:
    def mock_provisioner():
        m = Mock()
        m.provision.side_effect = ValueError("value error")
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/provision", json=provision_request)

    assert response.status_code == 500
    assert response.json() == {"error": "value error"}
    app.dependency_overrides = {}


def test_main_unprovision_exception() -> None:
    def mock_provisioner():
        m = Mock()
        m.unprovision.side_effect = ValueError("value error")
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/unprovision", json=provision_request)

    assert response.status_code == 500
    assert response.json() == {"error": "value error"}
    app.dependency_overrides = {}


def test_main_validate_exception() -> None:
    def mock_provisioner():
        m = Mock()
        m.validate.side_effect = ValueError("value error")
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/validate", json=provision_request)

    assert response.status_code == 500
    assert response.json() == {"error": "value error"}
    app.dependency_overrides = {}


def test_main_update_acl_exception() -> None:
    def mock_provisioner():
        m = Mock()
        m.update_acl.side_effect = ValueError("value error")
        return m

    app.dependency_overrides[get_provisioner] = mock_provisioner
    response = client.post("/v1/updateacl", json=update_acl_request)

    assert response.status_code == 500
    assert response.json() == {"error": "value error"}
    app.dependency_overrides = {}
