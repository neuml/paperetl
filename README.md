<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/paperetl/master/logo.png"/>
</p>

<p align="center">
    <b>ETL processes for medical and scientific papers</b>
</p>

<p align="center">
    <a href="https://github.com/neuml/paperetl/releases">
        <img src="https://img.shields.io/github/release/neuml/paperetl.svg?style=flat&color=success" alt="Version"/>
    </a>
    <a href="https://github.com/neuml/paperetl/releases">
        <img src="https://img.shields.io/github/release-date/neuml/paperetl.svg?style=flat&color=blue" alt="GitHub Release Date"/>
    </a>
    <a href="https://github.com/neuml/paperetl/issues">
        <img src="https://img.shields.io/github/issues/neuml/paperetl.svg?style=flat&color=success" alt="GitHub issues"/>
    </a>
    <a href="https://github.com/neuml/paperetl">
        <img src="https://img.shields.io/github/last-commit/neuml/paperetl.svg?style=flat&color=blue" alt="GitHub last commit"/>
    </a>
    <a href="https://github.com/neuml/paperetl/actions?query=workflow%3Abuild">
        <img src="https://github.com/neuml/paperetl/workflows/build/badge.svg" alt="Build Status"/>
    </a>
    <a href="https://coveralls.io/github/neuml/paperetl?branch=master">
        <img src="https://img.shields.io/coverallsCoverage/github/neuml/paperetl" alt="Coverage Status">
    </a>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

paperetl is an ETL library for processing medical and scientific papers.

![architecture](https://raw.githubusercontent.com/neuml/paperetl/master/images/architecture.png#gh-light-mode-only)
![architecture](https://raw.githubusercontent.com/neuml/paperetl/master/images/architecture-dark.png#gh-dark-mode-only)

paperetl supports the following sources:

- Full PDF articles
- [PubMed XML](https://pubmed.ncbi.nlm.nih.gov/download/)
- [ArXiv XML](https://info.arxiv.org/help/api/basics.html)
- [Text Encoding Initiative (TEI) XML](https://grobid.readthedocs.io/en/latest/TEI-encoding-of-results/)
- CSV with article metadta

paperetl supports the following storage options for parsed articles.

- SQLite
- Elasticsearch
- JSON files
- YAML files

## Installation

The easiest way to install is via pip and PyPI

```
pip install paperetl
```

Python 3.10+ is supported. Using a Python [virtual environment](https://docs.python.org/3/library/venv.html) is recommended.

paperetl can also be installed directly from GitHub to access the latest, unreleased features.

```
pip install git+https://github.com/neuml/paperetl
```

### Additional dependencies

PDF parsing relies on an existing GROBID instance to be up and running. It is assumed that this is running locally on the ETL server. This is only
necessary for PDF files.

- [GROBID install instructions](https://grobid.readthedocs.io/en/latest/Install-Grobid/)
- [GROBID start service](https://grobid.readthedocs.io/en/latest/Grobid-service/)

_Note: In some cases, the GROBID engine pool can be exhausted, resulting in a 503 error. This can be fixed by increasing `concurrency` and/or `poolMaxWait` in the [GROBID configuration file](https://grobid.readthedocs.io/en/latest/Configuration/#service-configuration)._

### Docker

A Dockerfile with commands to install paperetl, all dependencies and scripts are available in this repository.

```
wget https://raw.githubusercontent.com/neuml/paperetl/master/docker/Dockerfile
docker build -t paperetl -f Dockerfile .
docker run --name paperetl --rm -it paperetl
```

This will bring up a paperetl command shell. Standard Docker commands can be used to copy files over or commands can be run directly in the shell to retrieve input content.

## Examples

### Notebooks

| Notebook  | Description  |       |
|:----------|:-------------|------:|
| [Introducing paperetl](https://github.com/neuml/paperetl/blob/master/examples/01_Introducing_paperetl.ipynb) | Overview of the functionality provided by paperetl | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neuml/paperetl/blob/master/examples/01_Introducing_paperetl.ipynb) |

### Load Articles into SQLite

The following example shows how to use paperetl to load a set of medical/scientific articles into a SQLite database.

1. Download the desired medical/scientific articles in a local directory. For this example, it is assumed the articles are in a directory named `paperetl/data`

2. Build the database

    ```
    python -m paperetl.file paperetl/data paperetl/models
    ```

Once complete, there will be an articles.sqlite file in paperetl/models

### Load into Elasticsearch

Elasticsearch is also a supported datastore as shown below. This example assumes Elasticsearch is running locally, change the URL to a remote server as appropriate.

```
python -m paperetl.file paperetl/data http://localhost:9200
```

Once complete, there will be an articles index in Elasticsearch with the metadata and full text stored.

### Convert articles to JSON/YAML

paperetl can also be used to convert articles into JSON or YAML files. This is useful if the data is to be fed into another system or for manual inspection/debugging of a single file.

JSON:

```
python -m paperetl.file paperetl/data json://paperetl/json
```

YAML:

```
python -m paperetl.file paperetl/data yaml://paperetl/yaml
```

Converted files will be stored in paperetl/(json|yaml)
