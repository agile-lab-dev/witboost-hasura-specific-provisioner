# Hasura Specific Provisioner

This Python microservice implements the Witboost Specific Provisioner interface for GraphQL Output Ports based on Hasura.

## Repository structure

The Python project for the microservice is in the `hasura-specific-provisioner` subdirectory; this is probably what you're interested in. It contains the code, the tests, the docs, etc.

The rest of the contents of the root of the repository are mostly support scripts and configuration files for the GitLab CI, gitignore, etc.

## Developing

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

## Additional references

- To configure the `OpenTelemetry framework` refer to the [OpenTelemetry Setup](hasura-specific-provisioner/docs/opentelemetry.md).
- To build an `image` and run the `docker container` refer to [Docker Setup](hasura-specific-provisioner/docs/docker.md).
