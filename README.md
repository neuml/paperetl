<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/paperetl/master/logo.png"/>
</p>

<h3 align="center">
    <p>ETL processes for medical and scientific papers</p>
</h3>

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
        <img src="https://img.shields.io/coveralls/github/neuml/paperetl" alt="Coverage Status">
    </a>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

paperetl is an ETL library for processing medical and scientific papers. It supports the following sources:

- [CORD-19](https://www.semanticscholar.org/cord19)
- PDF articles

paperetl supports the following databases for storing articles:

- SQLite
- Elasticsearch
- JSON files
- YAML files

## Installation

The easiest way to install is via pip and PyPI

    pip install paperetl

You can also install paperetl directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/paperetl

Python 3.6+ is supported

### Additional dependencies

Study design detection uses scispacy and can be installed via:

    pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.5/en_core_sci_md-0.2.5.tar.gz

PDF parsing relies on an existing GROBID instance to be up and running. It is assumed that this is running locally on the ETL server. This is not
necessary for the CORD-19 dataset.

- [GROBID install instructions](https://grobid.readthedocs.io/en/latest/Install-Grobid/)
- [GROBID start service](https://grobid.readthedocs.io/en/latest/Grobid-service/)

### Docker

A Docker image with paperetl, all dependencies and scripts pre-installed is available in this repository.

Clone this git repository and run the following to start the Docker image.

```bash
docker build -t paperetl -f docker/Dockerfile .
docker run --name paperetl --rm -i -t paperetl
```

This will bring up a paperetl command shell. Standard Docker commands can be used to copy files over or commands can be run directly in the shell to retrieve input content. All scripts in the following examples are available in this environment.

## Examples

### Notebooks

| Notebook  |  Description |
|:----------|:-------------|
| [CORD-19 Article Entry Dates](https://www.kaggle.com/davidmezzetti/cord-19-article-entry-dates) | Generates CORD-19 entry-dates.csv file |
| [CORD-19 ETL](https://www.kaggle.com/davidmezzetti/cord-19-etl) | Builds an article.sqlite database for CORD-19 data |

### Load CORD-19 into SQLite

The following example shows how to use paperetl to load the CORD-19 dataset into a SQLite database.

1. Download and extract the dataset from [Allen Institute for AI CORD-19 Release Page](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html).

    ```bash
    scripts/getcord19.sh cord19/data
    ```

    The script above retrieves and unpacks the latest copy of CORD-19 into a directory named `cord19/data`. An optional second argument sets a specific date of the dataset in the format YYYY-MM-DD (ex. 2021-01-01) which defaults to the latest date.

2. Download [study design model](https://github.com/neuml/paperetl/releases/download/v1.2.0/study.tar.gz)

    ```bash
    scripts/getstudy.sh cord19/models
    ```

    The script above retrieves and unpacks a copy of the study model into a directory named `cord19/models`.

    The [study design model](https://www.kaggle.com/davidmezzetti/cord19-study-design) with training data is also available on Kaggle.

3. Generate entry-dates.csv for current version of the dataset

    ```bash
    python -m paperetl.cord19.entry cord19/data
    ```

    An optional second argument sets a specific date of the dataset in the format YYYY-MM-DD (ex. 2021-01-01) which defaults of the latest
    date. This should match the date used in Step 1.

    A version of [entry-dates.csv](https://www.kaggle.com/davidmezzetti/cord-19-article-entry-dates/output) is also available on Kaggle.

4. Build database

    ```bash
    python -m paperetl.cord19 cord19/data cord19/models cord19/models
    ```

Once complete, there will be an articles.sqlite file in cord19/models

### Load PDF Articles into SQLite

The following example shows how to use paperetl to load a set of medical/scientific pdf articles into a SQLite database.

1. Download the desired medical/scientific articles in a local directory. For this example, it is assumed the articles are in a directory named `paperetl/data`

2. Download [study design model](https://github.com/neuml/paperetl/releases/download/v1.2.0/study.tar.gz)

    ```bash
    scripts/getstudy.sh paperetl/models
    ```

    The [study design model](https://www.kaggle.com/davidmezzetti/cord19-study-design) with training data can also be found on Kaggle.

3. Build the database

    ```bash
    python -m paperetl.file paperetl/data paperetl/models paperetl/models
    ```

Once complete, there will be an articles.sqlite file in paperetl/models

### Load into Elasticsearch

Both of the examples above also support storing data in Elasticsearch with the following changes. These examples assume Elasticsearch is running locally, change the URL to a remote server as appropriate.

CORD-19:

    python -m paperetl.cord19 cord19/data http://localhost:9200

PDF Articles:

    python -m paperetl.file paperetl/data http://localhost:9200 paperetl/models

Once complete, there will be an articles index in elasticsearch with the metadata and full text stored.

### Convert PDF articles to JSON/YAML

paperetl can also be used to convert PDF articles into JSON or YAML files. This is useful if the data is to be fed into another system or for manual inspection/debugging of a single file.

JSON:

    python -m paperetl.file paperetl/data json://paperetl/json paperetl/models

YAML:

    python -m paperetl.file paperetl/data yaml://paperetl/yaml paperetl/models

Converted files will be stored in paperetl/(json|yaml)
