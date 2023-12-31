#!/bin/bash

echo -e "Uvicorn server initialization...\n"

PORT="${SERVICE_PORT:-5002}"
LOG_CONFIG="${LOG_CFG:-/app/logging.yaml}"

if [[ $1 = open_telemetry_activation ]];
then
    # The following configuration is set for the Dockerfile
    # If you want to test the service locally, change the IP address to 'localhost'
    echo -e "OpenTelemetry activation...\n"

    exec opentelemetry-instrument uvicorn src.main:app --host 0.0.0.0 --port "${PORT}" --log-config "${LOG_CONFIG}"

else
    # The following configuration is set for the Dockerfile
    # If you want to test the service locally, change the IP address to 'localhost'
    exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT}" --log-config "${LOG_CONFIG}"

fi
