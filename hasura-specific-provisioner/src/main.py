from __future__ import annotations

import logging
from typing import Union

from fastapi import FastAPI
from starlette import status
from starlette.responses import Response

import src
from src.dependencies import (
    HasuraProvisionerDep,
    UnpackedProvisioningRequestDep,
    UnpackedUpdateAclRequestDep,
)
from src.models import (
    ProvisioningStatus,
    SystemError,
    ValidationError,
    ValidationRequest,
    ValidationResult,
    ValidationStatus,
)

app = FastAPI(
    title="Hasura Specific Provisioner Microservice",
    description="Microservice responsible to handle provisioning and access control requests for Hasura-based data product components.",  # noqa: E501
    version=src.__version__,
    servers=[{"url": "/"}],
)

_logger = logging.getLogger(__name__)


@app.post(
    "/v1/provision",
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def provision(
    unpacked_request: UnpackedProvisioningRequestDep,
    response: Response,
    provisioner: HasuraProvisionerDep,
) -> Union[ProvisioningStatus, str, ValidationError, SystemError]:
    """
    Deploy a data product or a single component starting from a provisioning descriptor
    """
    try:
        if isinstance(unpacked_request, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return unpacked_request
        data_product, hasura_output_port, source_output_port = unpacked_request
        provisioning_result = provisioner.provision(
            data_product, hasura_output_port, source_output_port
        )
        if isinstance(provisioning_result, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return provisioning_result
        if isinstance(provisioning_result, ProvisioningStatus):
            response.status_code = status.HTTP_200_OK
            return provisioning_result
        else:
            raise Exception(
                "Unknown error during provisioning; check with the platform team."
            )
    except Exception as ex:
        _logger.exception("Exception in /v1/provision")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SystemError(error=str(ex))


@app.get(
    "/v1/provision/{token}/status",
    responses={
        "200": {"model": ProvisioningStatus},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def get_status(
    token: str,
    response: Response,
) -> Union[ProvisioningStatus, ValidationError, SystemError]:
    """
    Get the status for a provisioning request
    """
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return SystemError(error="Not implemented")


@app.post(
    "/v1/unprovision",
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def unprovision(
    unpacked_request: UnpackedProvisioningRequestDep,
    response: Response,
    provisioner: HasuraProvisionerDep,
) -> Union[ProvisioningStatus, str, ValidationError, SystemError]:
    """
    Undeploy a data product or a single component given the provisioning descriptor relative to the latest complete provisioning request
    """  # noqa: E501
    try:
        if isinstance(unpacked_request, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return unpacked_request
        data_product, hasura_output_port, source_output_port = unpacked_request
        provisioning_result = provisioner.unprovision(
            data_product, hasura_output_port, source_output_port
        )
        if isinstance(provisioning_result, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return provisioning_result
        if isinstance(provisioning_result, ProvisioningStatus):
            response.status_code = status.HTTP_200_OK
            return provisioning_result
        else:
            raise Exception(
                "Unknown error during provisioning; check with the platform team."
            )
    except Exception as ex:
        _logger.exception("Exception in /v1/unprovision")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SystemError(error=str(ex))


@app.post(
    "/v1/updateacl",
    responses={
        "200": {"model": ProvisioningStatus},
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def updateacl(
    unpacked_request: UnpackedUpdateAclRequestDep,
    response: Response,
    provisioner: HasuraProvisionerDep,
) -> Union[ProvisioningStatus, str, ValidationError, SystemError]:
    """
    Request the access to a specific provisioner component
    """
    try:
        if isinstance(unpacked_request, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return unpacked_request
        data_product, hasura_output_port, source_output_port, refs = unpacked_request
        provisioning_result = provisioner.update_acl(
            data_product, hasura_output_port, source_output_port, refs
        )
        if isinstance(provisioning_result, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return provisioning_result
        if isinstance(provisioning_result, ProvisioningStatus):
            response.status_code = status.HTTP_200_OK
            return provisioning_result
        else:
            raise Exception(
                "Unknown error during provisioning; check with the platform team."
            )
    except Exception as ex:
        _logger.exception("Exception in /v1/updateacl")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SystemError(error=str(ex))


@app.post(
    "/v1/validate",
    responses={"200": {"model": ValidationResult}, "500": {"model": SystemError}},
    tags=["SpecificProvisioner"],
)
def validate(
    unpacked_request: UnpackedProvisioningRequestDep,
    response: Response,
    provisioner: HasuraProvisionerDep,
) -> Union[ValidationResult, SystemError]:
    """
    Validate a provisioning request
    """
    try:
        if isinstance(unpacked_request, ValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ValidationResult(valid=False, error=unpacked_request)
        data_product, hasura_output_port, source_output_port = unpacked_request
        validation_result = provisioner.validate(
            data_product, hasura_output_port, source_output_port
        )
        response.status_code = status.HTTP_200_OK
        return validation_result
    except Exception as ex:
        _logger.exception("Exception in /v1/validate")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SystemError(error=str(ex))


@app.post(
    "/v2/validate",
    responses={
        "202": {"model": str},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def async_validate(
    body: ValidationRequest,
    response: Response,
) -> Union[None, str, ValidationError, SystemError]:
    """
    Validate a deployment request
    """
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return SystemError(error="Not implemented")


@app.get(
    "/v2/validate/{token}/status",
    responses={
        "200": {"model": ValidationStatus},
        "400": {"model": ValidationError},
        "500": {"model": SystemError},
    },
    tags=["SpecificProvisioner"],
)
def get_validation_status(
    token: str,
    response: Response,
) -> Union[ValidationStatus, ValidationError, SystemError]:
    """
    Get the status for a provisioning request
    """
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return SystemError(error="Not implemented")
