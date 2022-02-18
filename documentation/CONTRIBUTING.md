# How to contribute

To contribute, please fork the repository, add your changes to the code, and submit a pull request for review.

Prior to opening a pull request, all code should be formatted with `black` and `isort`, linted with `flake8`, and tested with `pytest`. Any issues raised by these tools should be resolved, or the lint and test checks in continuous integration will fail. Installing the pre-commit hooks as shown below will ensure that autoformatting and linting are run prior to new commits, but tests will need to be run separately.

To start developing locally, read through the [development guide](#development-guide) below!

# Development guide

## Setup

**1) [Follow regular installation instructions](../README.md#installation)**

**2) Install development dependencies**

```
pip install -e mugen[development]
```

**3) Download [Visual Studio Code](https://code.visualstudio.com/)**

It's recommended to use Visual Studio Code to take advantage of their integrated tooling.

**4) Configure Visual Studio Code**

In Visual Studio Code's Python settings:

-   Set the formatter to `black`
-   Set the imports sorter to `isort`
-   Enable flake8 linting
-   Enable format on save

Open Visual Studio Code's `settings.json` directly, and under the `[python]` section add the `organizeImports` code action on save:

```
"[python]": {
    "editor.codeActionsOnSave": {
        "source.organizeImports": true,
    },
},
```

If there is no python section, add it at the top level.

The settings above will ensure essential formatting and linting is performed automatically whenever a file is saved.

**5) Add pre-commit hooks**

```
pre-commit install
```

**6) Install [act](https://github.com/nektos/act)**

```
brew install act
```

Act enables testing Github Actions workflows locally.

## Linting and Testing

**Autoformat code with black**

```
black mugen scripts tests
```

**Autosort imports with isort**

```
isort
```

**Lint code with flake8**

```
flake8
```

**Run the test suite**

```
pytest
```

**Run the pre-commit hooks**

```
pre-commit run --all-files
```

This runs `black`, `isort`, and `flake8`

**Run a workflow locally**

```
act pull_request
```

**Run a specific workflow job locally**

```
act -j lint
```
