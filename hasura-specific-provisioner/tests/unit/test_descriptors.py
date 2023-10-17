from datetime import datetime, timezone
from textwrap import dedent

from src.common.model.descriptor import (
    DataProduct,
    HasuraOutputPort,
    HasuraOutputPortSpecific,
    OutputPort,
)

# we have long-ish dict literals here, black does a decent job of keeping them in check
# but does not always stay under 88 columns, so ignore E051 for this file
# ruff: noqa: E501


descriptor_yaml_ok: str = dedent(
    """
dataProduct:
    dataProductOwnerDisplayName: DP Owner
    environment: development
    domain: healthcare
    kind: dataproduct
    domainId: urn:dmb:dmn:healthcare
    id: urn:dmb:dp:healthcare:vaccinations:0
    description: DP about vaccinations
    devGroup: popeye
    ownerGroup: vaccinations_agilelab.it
    dataProductOwner: user:dp.owner_agilelab.it
    email: dp.owner@agilelab.it
    version: 0.1.0
    fullyQualifiedName: Vaccinations
    name: Vaccinations
    informationSLA: 2BD
    maturity: Tactical
    useCaseTemplateId: urn:dmb:utm:dataproduct-template:0.0.0
    infrastructureTemplateId: urn:dmb:itm:dataproduct-provisioner:1
    billing: {}
    tags: []
    specific: {}
    components:
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload
        description: Airbyte workload
        name: Airbyte Workload
        fullyQualifiedName: Airbyte Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:airbyte-provisioner:0
        useCaseTemplateId: urn:dmb:utm:airbyte-standard:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
          - urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload
        platform: Snowflake
        technology: airbyte
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          source:
            name: healthcare.vaccinations.0.File
            connectionConfiguration:
              url: https://storage.googleapis.com/covid19-open-data/v3/latest/vaccinations.csv
              format: csv
              provider:
                storage: HTTPS
                user_agent: true
              dataset_name: vaccinations_raw
          destination:
            name: healthcare.vaccinations.0.Snowflake
            connectionConfiguration:
              database: HEALTHCARE
              schema: VACCINATIONS_0
          connection:
            name: healthcare.vaccinations.0.Vaccinations File <> Snowflake
            dbtGitUrl: https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository/sandbox/vaccinations/dbt_transformation_workload.git
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:airflow-workload
        description: Scheduling for the Vaccinations DP
        name: Airflow Workload
        fullyQualifiedName: Airflow Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-airflow-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-airflow-workload-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
          - urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          scheduleCron: 5 5 * * *
          dagName: airbyte_snowflake_dag.py
          destinationPath: dags/
          sourcePath: source/
          bucketName: aws-ia-mwaa-eu-west-1-621415221771
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:asdasd
        description: qqqq
        name: asdasd
        fullyQualifiedName: qweqwe
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-snowflake-sql-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-workload-snowflake-sql-template:0.0.0
        dependsOn: []
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific: {}
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload
        description: DBT workload on Snowflake via Airbyte
        name: DBT Transformation Workload
        fullyQualifiedName: DBT Transformation Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-dbt-transformation-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-workload-dbt-transformation-template:0.0.0
        dependsOn: []
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          dbtProjectName: dmb_dbt_transform
          gitUrl: https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository/sandbox/vaccinations/dbt_transformation_workload.git
      - kind: outputport
        id: urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
        description: Output Port for vaccinations data using Snowflake
        name: Snowflake Output Port
        fullyQualifiedName: Snowflake Output Port
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:snowflake-outputport-provisioner:0
        useCaseTemplateId: urn:dmb:utm:snowflake-outputport-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
        platform: Snowflake
        technology: Snowflake
        outputPortType: SQL
        creationDate: 2023-03-02T15:54:17.447Z
        startDate: 2023-03-02T15:54:17.447Z
        dataContract:
          schema:
            - name: date
              dataType: DATE
            - name: location_key
              dataType: TEXT
              constraint: PRIMARY_KEY
            - name: new_persons_vaccinated
              dataType: NUMBER
            - name: new_persons_fully_vaccinated
              dataType: NUMBER
            - name: new_vaccine_doses_administered
              dataType: NUMBER
            - name: cumulative_persons_vaccinated
              dataType: NUMBER
            - name: cumulative_persons_fully_vaccinated
              dataType: NUMBER
            - name: cumulative_vaccine_doses_administered
              dataType: NUMBER
        tags: []
        sampleData: {}
        semanticLinking: []
        specific:
          viewName: vaccinations_clean_view
          tableName: vaccinations_clean
          database: HEALTHCARE
          schema: VACCINATIONS_0
      - kind: storage
        id: urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
        description: Vaccinations data storage (schema) in Snowflake
        name: Snowflake Storage Vaccinations
        fullyQualifiedName: Snowflake Storage Vaccinations
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:snowflake-storage-provisioner:0
        useCaseTemplateId: urn:dmb:utm:snowflake-storage-template:0.0.0
        dependsOn: []
        platform: Snowflake
        technology: Snowflake
        StorageType: Database
        tags: []
        specific:
          database: HEALTHCARE
          schema: VACCINATIONS_0
      - kind: outputport
        id: urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port
        description: Output Port for vaccinations data using Hasura
        name: Hasura Output Port
        fullyQualifiedName: Hasura Output Port
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:hasura-outputport-provisioner:0
        useCaseTemplateId: urn:dmb:utm:hasura-outputport-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
        platform: Hasura
        technology: Hasura
        outputPortType: GraphQL
        creationDate: 2023-06-12T12:52:11.737Z
        startDate: 2023-06-12T12:52:11.737Z
        dataContract:
          schema:
            - name: date
              dataType: DATE
            - name: location_key
              dataType: TEXT
              constraint: PRIMARY_KEY
            - name: new_persons_vaccinated
              dataType: NUMBER
            - name: new_persons_fully_vaccinated
              dataType: NUMBER
            - name: new_vaccine_doses_administered
              dataType: NUMBER
            - name: cumulative_persons_vaccinated
              dataType: NUMBER
            - name: cumulative_persons_fully_vaccinated
              dataType: NUMBER
            - name: cumulative_vaccine_doses_administered
              dataType: NUMBER
        tags: []
        sampleData: {}
        semanticLinking: []
        specific:
            customTableName: healthcare_vaccinations_0_hasuraoutputport_vaccinations
            select: healthcare_vaccinations_0_hasuraoutputport_vaccinations_select
            selectByPk: healthcare_vaccinations_0_hasuraoutputport_vaccinations_by_pk
            selectAggregate: healthcare_vaccinations_0_hasuraoutputport_vaccinations_agg
            selectStream: healthcare_vaccinations_0_hasuraoutputport_vaccinations_stream
componentIdToProvision: urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port
"""
)
data_product_ok = DataProduct(
    id="urn:dmb:dp:healthcare:vaccinations:0",
    name="Vaccinations",
    domain="healthcare",
    environment="development",
    version="0.1.0",
    dataProductOwner="user:dp.owner_agilelab.it",
    devGroup="popeye",
    ownerGroup="vaccinations_agilelab.it",
    specific={},
    components=[
        {
            "kind": "workload",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload",
            "description": "Airbyte workload",
            "name": "Airbyte Workload",
            "fullyQualifiedName": "Airbyte Workload",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:airbyte-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:airbyte-standard:0.0.0",
            "dependsOn": [
                "urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations",
                "urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload",
            ],
            "platform": "Snowflake",
            "technology": "airbyte",
            "workloadType": "batch",
            "connectionType": "DataPipeline",
            "tags": [],
            "readsFrom": [],
            "specific": {
                "source": {
                    "name": "healthcare.vaccinations.0.File",
                    "connectionConfiguration": {
                        "url": "https://storage.googleapis.com/covid19-open-data/v3/latest/vaccinations.csv",
                        "format": "csv",
                        "provider": {"storage": "HTTPS", "user_agent": True},
                        "dataset_name": "vaccinations_raw",
                    },
                },
                "destination": {
                    "name": "healthcare.vaccinations.0.Snowflake",
                    "connectionConfiguration": {
                        "database": "HEALTHCARE",
                        "schema": "VACCINATIONS_0",
                    },
                },
                "connection": {
                    "name": "healthcare.vaccinations.0.Vaccinations File "
                    + "<> Snowflake",
                    "dbtGitUrl": "https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository"
                    + "/sandbox/vaccinations/dbt_transformation_workload.git",
                },
            },
        },
        {
            "kind": "workload",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:airflow-workload",
            "description": "Scheduling for the Vaccinations DP",
            "name": "Airflow Workload",
            "fullyQualifiedName": "Airflow Workload",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:aws-workload-airflow-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:aws-airflow-workload-template:0.0.0",
            "dependsOn": [
                "urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port",
                "urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload",
            ],
            "platform": "AWS",
            "technology": "airflow",
            "workloadType": "batch",
            "connectionType": "DataPipeline",
            "tags": [],
            "readsFrom": [],
            "specific": {
                "scheduleCron": "5 5 * * *",
                "dagName": "airbyte_snowflake_dag.py",
                "destinationPath": "dags/",
                "sourcePath": "source/",
                "bucketName": "aws-ia-mwaa-eu-west-1-621415221771",
            },
        },
        {
            "kind": "workload",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:asdasd",
            "description": "qqqq",
            "name": "asdasd",
            "fullyQualifiedName": "qweqwe",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:aws-workload-snowflake-sql-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:aws-workload-snowflake-sql-template:0.0.0",
            "dependsOn": [],
            "platform": "AWS",
            "technology": "airflow",
            "workloadType": "batch",
            "connectionType": "DataPipeline",
            "tags": [],
            "readsFrom": [],
            "specific": {},
        },
        {
            "kind": "workload",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload",
            "description": "DBT workload on Snowflake via Airbyte",
            "name": "DBT Transformation Workload",
            "fullyQualifiedName": "DBT Transformation Workload",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:aws-workload-dbt-transformation-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:aws-workload-dbt-transformation-template:0.0.0",
            "dependsOn": [],
            "platform": "AWS",
            "technology": "airflow",
            "workloadType": "batch",
            "connectionType": "DataPipeline",
            "tags": [],
            "readsFrom": [],
            "specific": {
                "dbtProjectName": "dmb_dbt_transform",
                "gitUrl": "https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository/sandbox/vaccinations/dbt_transformation_workload.git",
            },
        },
        {
            "kind": "outputport",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port",
            "description": "Output Port for vaccinations data using Snowflake",
            "name": "Snowflake Output Port",
            "fullyQualifiedName": "Snowflake Output Port",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:snowflake-outputport-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:snowflake-outputport-template:0.0.0",
            "dependsOn": [
                "urn:dmb:cmp:healthcare:vaccinations:0:"
                + "snowflake-storage-vaccinations"
            ],
            "platform": "Snowflake",
            "technology": "Snowflake",
            "outputPortType": "SQL",
            "creationDate": datetime(
                2023, 3, 2, 15, 54, 17, 447000, tzinfo=timezone.utc
            ),
            "startDate": datetime(2023, 3, 2, 15, 54, 17, 447000, tzinfo=timezone.utc),
            "dataContract": {
                "schema": [
                    {"name": "date", "dataType": "DATE"},
                    {
                        "name": "location_key",
                        "dataType": "TEXT",
                        "constraint": "PRIMARY_KEY",
                    },
                    {"name": "new_persons_vaccinated", "dataType": "NUMBER"},
                    {"name": "new_persons_fully_vaccinated", "dataType": "NUMBER"},
                    {"name": "new_vaccine_doses_administered", "dataType": "NUMBER"},
                    {"name": "cumulative_persons_vaccinated", "dataType": "NUMBER"},
                    {
                        "name": "cumulative_persons_fully_vaccinated",
                        "dataType": "NUMBER",
                    },
                    {
                        "name": "cumulative_vaccine_doses_administered",
                        "dataType": "NUMBER",
                    },
                ]
            },
            "tags": [],
            "sampleData": {},
            "semanticLinking": [],
            "specific": {
                "viewName": "vaccinations_clean_view",
                "tableName": "vaccinations_clean",
                "database": "HEALTHCARE",
                "schema": "VACCINATIONS_0",
            },
        },
        {
            "kind": "storage",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:"
            + "snowflake-storage-vaccinations",
            "description": "Vaccinations data storage (schema) in Snowflake",
            "name": "Snowflake Storage Vaccinations",
            "fullyQualifiedName": "Snowflake Storage Vaccinations",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:snowflake-storage-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:snowflake-storage-template:0.0.0",
            "dependsOn": [],
            "platform": "Snowflake",
            "technology": "Snowflake",
            "StorageType": "Database",
            "tags": [],
            "specific": {"database": "HEALTHCARE", "schema": "VACCINATIONS_0"},
        },
        {
            "kind": "outputport",
            "id": "urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port",
            "description": "Output Port for vaccinations data using Hasura",
            "name": "Hasura Output Port",
            "fullyQualifiedName": "Hasura Output Port",
            "version": "0.0.0",
            "infrastructureTemplateId": "urn:dmb:itm:hasura-outputport-provisioner:0",
            "useCaseTemplateId": "urn:dmb:utm:hasura-outputport-template:0.0.0",
            "dependsOn": [
                "urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port"
            ],
            "platform": "Hasura",
            "technology": "Hasura",
            "outputPortType": "GraphQL",
            "creationDate": datetime(
                2023, 6, 12, 12, 52, 11, 737000, tzinfo=timezone.utc
            ),
            "startDate": datetime(2023, 6, 12, 12, 52, 11, 737000, tzinfo=timezone.utc),
            "dataContract": {
                "schema": [
                    {"name": "date", "dataType": "DATE"},
                    {
                        "name": "location_key",
                        "dataType": "TEXT",
                        "constraint": "PRIMARY_KEY",
                    },
                    {"name": "new_persons_vaccinated", "dataType": "NUMBER"},
                    {"name": "new_persons_fully_vaccinated", "dataType": "NUMBER"},
                    {"name": "new_vaccine_doses_administered", "dataType": "NUMBER"},
                    {"name": "cumulative_persons_vaccinated", "dataType": "NUMBER"},
                    {
                        "name": "cumulative_persons_fully_vaccinated",
                        "dataType": "NUMBER",
                    },
                    {
                        "name": "cumulative_vaccine_doses_administered",
                        "dataType": "NUMBER",
                    },
                ]
            },
            "tags": [],
            "sampleData": {},
            "semanticLinking": [],
            "specific": {
                "customTableName": "healthcare_vaccinations_0_hasuraoutputport_vaccinations",
                "select": "healthcare_vaccinations_0_hasuraoutputport_vaccinations_select",
                "selectByPk": "healthcare_vaccinations_0_hasuraoutputport_vaccinations_by_pk",
                "selectAggregate": "healthcare_vaccinations_0_hasuraoutputport_vaccinations_agg",
                "selectStream": "healthcare_vaccinations_0_hasuraoutputport_vaccinations_stream",
            },
        },
    ],
)
hasura_op_ok = HasuraOutputPort(
    id="urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port",
    name="Hasura Output Port",
    fullyQualifiedName="Hasura Output Port",
    description="Output Port for vaccinations data using Hasura",
    kind="outputport",
    version="0.0.0",
    infrastructureTemplateId="urn:dmb:itm:hasura-outputport-provisioner:0",
    useCaseTemplateId="urn:dmb:utm:hasura-outputport-template:0.0.0",
    dependsOn=["urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port"],
    platform="Hasura",
    technology="Hasura",
    outputPortType="GraphQL",
    creationDate=datetime(2023, 6, 12, 12, 52, 11, 737000, tzinfo=timezone.utc),
    startDate=datetime(2023, 6, 12, 12, 52, 11, 737000, tzinfo=timezone.utc),
    tags=[],
    sampleData={},
    semanticLinking=[],
    specific=HasuraOutputPortSpecific(
        customTableName="healthcare_vaccinations_0_hasuraoutputport_vaccinations",
        select="healthcare_vaccinations_0_hasuraoutputport_vaccinations_select",
        selectByPk="healthcare_vaccinations_0_hasuraoutputport_vaccinations_by_pk",
        selectAggregate="healthcare_vaccinations_0_hasuraoutputport_vaccinations_agg",
        selectStream="healthcare_vaccinations_0_hasuraoutputport_vaccinations_stream",
    ),
)
snowflake_op_ok = OutputPort(
    id="urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port",
    name="Snowflake Output Port",
    fullyQualifiedName="Snowflake Output Port",
    description="Output Port for vaccinations data using Snowflake",
    kind="outputport",
    version="0.0.0",
    infrastructureTemplateId="urn:dmb:itm:snowflake-outputport-provisioner:0",
    useCaseTemplateId="urn:dmb:utm:snowflake-outputport-template:0.0.0",
    dependsOn=["urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations"],
    platform="Snowflake",
    technology="Snowflake",
    outputPortType="SQL",
    creationDate=datetime(2023, 3, 2, 15, 54, 17, 447000, tzinfo=timezone.utc),
    startDate=datetime(2023, 3, 2, 15, 54, 17, 447000, tzinfo=timezone.utc),
    tags=[],
    sampleData={},
    semanticLinking=[],
    specific={
        "viewName": "vaccinations_clean_view",
        "tableName": "vaccinations_clean",
        "database": "HEALTHCARE",
        "schema": "VACCINATIONS_0",
    },
)

descriptor_yaml_validation_ko: str = dedent(
    """
dataProduct:
    dataProductOwnerDisplayName: DP Owner
    environment: development
    domain: healthcare
    kind: dataproduct
    domainId: urn:dmb:dmn:healthcare
    id: urn:dmb:dp:healthcare:vaccinations:0
    description: DP about vaccinations
    devGroup: popeye
    ownerGroup: vaccinations_agilelab.it
    dataProductOwner: user:dp.owner_agilelab.it
    email: dp.owner@agilelab.it
    version: 0.1.0
    fullyQualifiedName: Vaccinations
    name: Vaccinations
    informationSLA: 2BD
    maturity: Tactical
    useCaseTemplateId: urn:dmb:utm:dataproduct-template:0.0.0
    infrastructureTemplateId: urn:dmb:itm:dataproduct-provisioner:1
    billing: {}
    tags: []
    specific: {}
    components:
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload
        description: Airbyte workload
        name: Airbyte Workload
        fullyQualifiedName: Airbyte Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:airbyte-provisioner:0
        useCaseTemplateId: urn:dmb:utm:airbyte-standard:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
          - urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload
        platform: Snowflake
        technology: airbyte
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          source:
            name: healthcare.vaccinations.0.File
            connectionConfiguration:
              url: https://storage.googleapis.com/covid19-open-data/v3/latest/vaccinations.csv
              format: csv
              provider:
                storage: HTTPS
                user_agent: true
              dataset_name: vaccinations_raw
          destination:
            name: healthcare.vaccinations.0.Snowflake
            connectionConfiguration:
              database: HEALTHCARE
              schema: VACCINATIONS_0
          connection:
            name: healthcare.vaccinations.0.Vaccinations File <> Snowflake
            dbtGitUrl: https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository/sandbox/vaccinations/dbt_transformation_workload.git
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:airflow-workload
        description: Scheduling for the Vaccinations DP
        name: Airflow Workload
        fullyQualifiedName: Airflow Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-airflow-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-airflow-workload-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
          - urn:dmb:cmp:healthcare:vaccinations:0:airbyte-workload
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          scheduleCron: 5 5 * * *
          dagName: airbyte_snowflake_dag.py
          destinationPath: dags/
          sourcePath: source/
          bucketName: aws-ia-mwaa-eu-west-1-621415221771
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:asdasd
        description: qqqq
        name: asdasd
        fullyQualifiedName: qweqwe
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-snowflake-sql-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-workload-snowflake-sql-template:0.0.0
        dependsOn: []
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific: {}
      - kind: workload
        id: urn:dmb:cmp:healthcare:vaccinations:0:dbt-transformation-workload
        description: DBT workload on Snowflake via Airbyte
        name: DBT Transformation Workload
        fullyQualifiedName: DBT Transformation Workload
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:aws-workload-dbt-transformation-provisioner:0
        useCaseTemplateId: urn:dmb:utm:aws-workload-dbt-transformation-template:0.0.0
        dependsOn: []
        platform: AWS
        technology: airflow
        workloadType: batch
        connectionType: DataPipeline
        tags: []
        readsFrom: []
        specific:
          dbtProjectName: dmb_dbt_transform
          gitUrl: https://gitlab.com/AgileDmbSandbox/popeye/mesh.repository/sandbox/vaccinations/dbt_transformation_workload.git
      - kind: outputport
        id: urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
        description: Output Port for vaccinations data using Snowflake
        name: Snowflake Output Port
        fullyQualifiedName: Snowflake Output Port
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:snowflake-outputport-provisioner:0
        useCaseTemplateId: urn:dmb:utm:snowflake-outputport-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
        platform: Snowflake
        technology: Snowflake
        outputPortType: SQL
        creationDate: 2023-03-02T15:54:17.447Z
        startDate: 2023-03-02T15:54:17.447Z
        dataContract:
          schema:
            - name: date
              dataType: DATE
            - name: location_key
              dataType: TEXT
              constraint: PRIMARY_KEY
            - name: new_persons_vaccinated
              dataType: NUMBER
            - name: new_persons_fully_vaccinated
              dataType: NUMBER
            - name: new_vaccine_doses_administered
              dataType: NUMBER
            - name: cumulative_persons_vaccinated
              dataType: NUMBER
            - name: cumulative_persons_fully_vaccinated
              dataType: NUMBER
            - name: cumulative_vaccine_doses_administered
              dataType: NUMBER
        tags: []
        sampleData: {}
        semanticLinking: []
        specific:
          viewName: vaccinations_clean_view
          tableName: vaccinations_clean
          database: HEALTHCARE
          schema: VACCINATIONS_0
      - kind: storage
        id: urn:dmb:cmp:healthcare:vaccinations:0:snowflake-storage-vaccinations
        description: Vaccinations data storage (schema) in Snowflake
        name: Snowflake Storage Vaccinations
        fullyQualifiedName: Snowflake Storage Vaccinations
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:snowflake-storage-provisioner:0
        useCaseTemplateId: urn:dmb:utm:snowflake-storage-template:0.0.0
        dependsOn: []
        platform: Snowflake
        technology: Snowflake
        StorageType: Database
        tags: []
        specific:
          database: HEALTHCARE
          schema: VACCINATIONS_0
      - kind: outputport
        id: urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port
        description: Output Port for vaccinations data using Hasura
        name: Hasura Output Port
        fullyQualifiedName: Hasura Output Port
        version: 0.0.0
        infrastructureTemplateId: urn:dmb:itm:hasura-outputport-provisioner:0
        useCaseTemplateId: urn:dmb:utm:hasura-outputport-template:0.0.0
        dependsOn:
          - urn:dmb:cmp:healthcare:vaccinations:0:snowflake-output-port
        platform: Hasura
        technology: Hasura
        outputPortType: GraphQL
        creationDate: 2023-06-12T12:52:11.737Z
        startDate: 2023-06-12T12:52:11.737Z
        dataContract:
          schema:
            - name: date
              dataType: DATE
            - name: location_key
              dataType: TEXT
              constraint: PRIMARY_KEY
            - name: new_persons_vaccinated
              dataType: NUMBER
            - name: new_persons_fully_vaccinated
              dataType: NUMBER
            - name: new_vaccine_doses_administered
              dataType: NUMBER
            - name: cumulative_persons_vaccinated
              dataType: NUMBER
            - name: cumulative_persons_fully_vaccinated
              dataType: NUMBER
            - name: cumulative_vaccine_doses_administered
              dataType: NUMBER
        tags: []
        sampleData: {}
        semanticLinking: []
        specific:
            customTableName: wrong_prefix_healthcare_vaccinations_0_hasuraoutputport_vaccinations
            select: wrong_prefix_healthcare_vaccinations_0_hasuraoutputport_vaccinations_select
            selectByPk: wrong_prefix_healthcare_vaccinations_0_hasuraoutputport_vaccinations_by_pk
            selectAggregate: wrong_prefix_duplicate_value
            selectStream: wrong_prefix_duplicate_value
componentIdToProvision: urn:dmb:cmp:healthcare:vaccinations:0:hasura-output-port
"""
)
