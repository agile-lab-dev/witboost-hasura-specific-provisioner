<p align="center">
    <a href="https://www.agilelab.it/witboost">
        <img src="docs/img/witboost_logo.svg" alt="witboost" width=600 >
    </a>
</p>

Designed by [Agile Lab](https://www.agilelab.it/), witboost is a versatile platform that addresses a wide range of sophisticated data engineering challenges. It enables businesses to discover, enhance, and productize their data, fostering the creation of automated data platforms that adhere to the highest standards of data governance. Want to know more about witboost? Check it out [here](https://www.agilelab.it/witboost) or [contact us!](https://www.agilelab.it/contacts)

This repository is part of our [Starter Kit](https://github.com/agile-lab-dev/witboost-starter-kit) meant to showcase witboost's integration capabilities and provide a "batteries-included" product.

# Hasura Specific Provisioner

- [Overview](#overview)
- [Building](#building)
- [Running](#running)
- [Configuring](#configuring)
- [Deploying](#deploying)
- [HLD](hld/HLD.md)
- [API specification](hasura-specific-provisioner/docs/API.md)

## Overview

This Python microservice implements the Witboost Specific Provisioner interface for GraphQL Output Ports based on Hasura.

### What's a Specific Provisioner?

A Specific Provisioner is a microservice which is in charge of deploying components that use a specific technology. When the deployment of a Data Product is triggered, the platform generates it descriptor and orchestrates the deployment of every component contained in the Data Product. For every such component the platform knows which Specific Provisioner is responsible for its deployment, and can thus send a provisioning request with the descriptor to it so that the Specific Provisioner can perform whatever operation is required to fulfill this request and report back the outcome to the platform.

You can learn more about how the Specific Provisioners fit in the broader picture [here](https://docs.witboost.agilelab.it/docs/p2_arch/p1_intro/#deploy-flow).

### Hasura

Hasura is an open-source, real-time GraphQL engine that simplifies and accelerates API development for web and mobile applications. It connects to your data sources like databases or REST services and automatically generates a GraphQL API, making it easier to query and manipulate data. Hasura's real-time capabilities enable instant updates to clients when data changes, enhancing the responsiveness of applications. It's a popular tool for developers looking to streamline the process of building dynamic and interactive applications by providing a unified and efficient way to access, manage, and synchronize data.

### Software stack

This microservice is written in Python 3.11, using FastAPI for the HTTP layer. Project is built with Poetry and supports packaging as Wheel and Docker image, ideal for Kubernetes deployments (which is the preferred option).

### Repository structure

The Python project for the microservice is in the `hasura-specific-provisioner` subdirectory; this is probably what you're interested in. It contains the code, the tests, the docs, etc.

The rest of the contents of the root of the repository are mostly support scripts and configuration files for the GitLab CI, gitignore, etc.

## Building

**Requirements:**

- Python 3.11
- Poetry

### Setup the Python environment

To set up a Python environment we use [Poetry](https://python-poetry.org/):
```
curl -sSL https://install.python-poetry.org | python3 -
```

> 📝 If you are on Windows, you probably want to use pipx instead:
> ```
> pipx install poetry
> ```

Once Poetry is installed and in your `$PATH`, you can execute the following:
```
poetry --version
```
If you see something like `Poetry (version x.x.x)`, your install is ready to use!

Install the dependencies defined in `hasura-specific-provisioner/pyproject.toml`:
```
cd hasura-specific-provisioner
poetry install
```
Poetry automatically creates a Python virtual environment in which the packages are installed; make sure to read the next section to enable it.

> 📝 If you are on Windows, you may get an error about Visual C++ missing; follow the instructions provided by Poetry to fix it.

### Use the Python environment

You just need to enable the Python virtual environment (venv) generated by Poetry:
```
source $(poetry env info --path)/bin/activate
```
As with any Python venv, your shell prompt will change to reflect the active venv.

You can also use:
```
poetry shell
```
Which spawns a subshell in the virtual environment; it is slighly different than the command above as this is not a login shell, hence your shell's profile file will likely be ignored.

### Setup the pre-commit hooks

Simply run:
```
pre-commit install
```
In case you need to commit and skip the pre-commit checks (eg, to push WIP code, or to test that the CI catches formatting issues), you can pass the `--no-verify` flag to `git commit`.

### Setup PyCharm

The recommended IDE is PyCharm, though other ones should work just fine.

In order to import the project, use the standard "Open..." dialog and point PyCharm to the `hasura-specific-provisioner` subdirectory, *not the repository root*. This ensures that PyCharm correctly identifies this as a Poetry project and prompts you to set it up as such.

### Docker build

The Docker image can be built with:

```
docker build .
```

More details can be found [here](hasura-specific-provisioner/docs/docker.md).

### Additional notes

**Application version:** the version for the project is automatically computed using information gathered from Git, using branch name and tags. Unless you are on a release branch `1.2.x` or a tag `v1.2.3` it will end up being `0.0.0`. You can follow this branch/tag convention or update the version computation to match your preferred strategy.

**CI/CD:** the pipeline is based on GitLab CI as that's what we use internally. It's configured by the `.gitlab-ci.yaml` file in the root of the repository. You can use that as a starting point for your customizations.

## Running

To run the server locally, use:

```bash
cd hasura-specific-provisioner
source $(poetry env info --path)/bin/activate # only needed if venv is not already enabled
uvicorn src.main:app --host 127.0.0.1 --port 8091
```

By default, the server binds to port 8091 on localhost. After it's up and running you can make provisioning requests to this address. You can also check the API documentation served [here](http://127.0.0.1:8091/docs).

## Configuring

Application configurations are handled with environment variables:

| Environment Variable | Description                                             |
|----------------------|---------------------------------------------------------|
| HASURA_URL           | URL of the Hasura instance                              |
| HASURA_ADMIN_SECRET  | The secret to use for authenticating to the Hasura      |
| HASURA_TIMEOUT       | The timeout to use when sending requests to Hasura      |
| ROLE_MAPPER_URL      | URL of the RoleMapper Micro Service                     |
| ROLE_MAPPER_TIMEOUT  | The timeout to use when sending requests to Role Mapper |
| SNOWFLAKE_HOST       | Snowflake host                                          |
| SNOWFLAKE_USER       | Snowflake user                                          |
| SNOWFLAKE_PASSWORD   | Snowflake password                                      |
| SNOWFLAKE_ROLE       | Snowflake role                                          |
| SNOWFLAKE_WAREHOUSE  | Snowflake warehouse                                     |

Those environment variables are already templated in the Helm chart (see below). Customize them according to your needs.

Logging is handled with the native Python logging module.

To configure the `OpenTelemetry framework` refer to the [OpenTelemetry Setup](hasura-specific-provisioner/docs/opentelemetry.md).

## Deploying

This microservice is meant to be deployed to a Kubernetes cluster with the included Helm chart and the scripts that can be found in the `helm` subdirectory. You can find more details [here](helm/README.md).

## License

This project is available under the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0); see [LICENSE](LICENSE) for full details.

## About us

<p align="center">
    <a href="https://www.agilelab.it">
        <img src="docs/img/agilelab_logo.jpg" alt="Agile Lab" width=600>
    </a>
</p>

Agile Lab creates value for its Clients in data-intensive environments through customizable solutions to establish performance driven processes, sustainable architectures, and automated platforms driven by data governance best practices.

Since 2014 we have implemented 100+ successful Elite Data Engineering initiatives and used that experience to create Witboost: a technology agnostic, modular platform, that empowers modern enterprises to discover, elevate and productize their data both in traditional environments and on fully compliant Data mesh architectures.

[Contact us](https://www.agilelab.it/contacts) or follow us on:
- [LinkedIn](https://www.linkedin.com/company/agile-lab/)
- [Instagram](https://www.instagram.com/agilelab_official/)
- [YouTube](https://www.youtube.com/channel/UCTWdhr7_4JmZIpZFhMdLzAA)
- [Twitter](https://twitter.com/agile__lab)
