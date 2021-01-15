# paperetl: ETL processes for medical and scientific papers

[![Version](https://img.shields.io/github/release/neuml/paperetl.svg?style=flat&color=success)](https://github.com/neuml/paperetl/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/neuml/paperetl.svg?style=flat&color=blue)](https://github.com/neuml/paperetl/releases)
[![GitHub issues](https://img.shields.io/github/issues/neuml/paperetl.svg?style=flat&color=success)](https://github.com/neuml/paperetl/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/neuml/paperetl.svg?style=flat&color=blue)](https://github.com/neuml/paperetl)
[![Build Status](https://github.com/neuml/paperetl/workflows/build/badge.svg)](https://github.com/neuml/paperetl/actions?query=workflow%3Abuild)
[![Coverage Status](https://img.shields.io/coveralls/github/neuml/paperetl)](https://coveralls.io/github/neuml/paperetl?branch=master)

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

## Additional dependencies
Study design detection uses scispacy and can be installed via:

    pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.5/en_core_sci_md-0.2.5.tar.gz

PDF parsing relies on an existing GROBID instance to be up and running. It is assumed that this is running locally on the ETL server. This is not
necessary for the CORD-19 dataset.

- [GROBID install instructions](https://grobid.readthedocs.io/en/latest/Install-Grobid/)
- [GROBID start service](https://grobid.readthedocs.io/en/latest/Grobid-service/)

## Examples

### Load CORD-19 into SQLite
The following example shows how to use paperetl to load the CORD-19 dataset into a SQLite database.

1. Download the latest dataset on the [Allen Institute for AI CORD-19 Release Page](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html). Go to the directory with the file and run the following commands.

    ```bash
    cd <download_path>
    tar -xvzf cord-19_$DATE.tar.gz
    tar -xvzf $DATE/document_parses.tar.gz -P .
    mv $DATE/metadata.csv .
    ```

    Where $DATE is the yyyy-mm-dd formatted date string in the file downloaded. Once completed, there should be a file named metadata.csv and a directory named document_parses.

2. Download study model

    ```bash
    wget -N https://github.com/neuml/paperetl/releases/download/v1.2.0/study.tar.gz -P /tmp
    tar -xvzf /tmp/study.tar.gz -C /tmp
    mv /tmp/paperetl/study/* ~/.cord19/models
    ```

    The [study design model](https://www.kaggle.com/davidmezzetti/cord19-study-design) with training data can also be found on Kaggle.

3. Download [latest entry-dates.csv](https://www.kaggle.com/davidmezzetti/cord-19-article-entry-dates/output) from Kaggle and place in `download path`

4. Build database

    ```bash
    python -m paperetl.cord19 <download_path>
    ```

Once complete, there will be an articles.sqlite file in ~/.cord19/models

See the [CORD-19 ETL](https://www.kaggle.com/davidmezzetti/cord-19-etl) notebook for a comprehensive example of paperetl in action.

### Load PDF Articles into SQLite
The following example shows how to use paperetl to load a set of medical/scientific pdf articles into a SQLite database.

1. Download the desired medical/scientific articles in a local directory. For this example, it is assumed the articles are in a directory named `/data/paperetl/data`

2. Download study model

    ```bash
    wget -N https://github.com/neuml/paperetl/releases/download/v1.2.0/study.tar.gz -P /data
    tar -xvzf /tmp/study.tar.gz -C /data
    ```

    The [study design model](https://www.kaggle.com/davidmezzetti/cord19-study-design) with training data can also be found on Kaggle.

3. Build the database

    ```bash
    python -m paperetl.file /data/paperetl/data /data/paperetl/models /data/paperetl/models
    ```

Once complete, there will be an articles.sqlite file in /data/paperetl/models

### Load into Elasticsearch
Both of the examples above also support storing data in Elasticsearch with the following changes. These examples assume Elasticsearch is running locally, change the URL to a remote server as appropriate.

CORD-19:

    python -m paperetl.cord19 <download_path> http://localhost:9200

PDF Articles:

    python -m paperetl.file /data/paperetl/data http://localhost:9200 /data/paperetl/models

Once complete, there will be an articles index in elasticsearch with the metadata and full text stored.

### Convert PDF articles to JSON/YAML
paperetl can also be used to convert PDF articles into JSON or YAML files. This is useful if the data is to be fed into another system or for manual inspection/debugging of a single file.

JSON:

    python -m paperetl.file /data/paperetl/data json:///data/paperetl/json /data/paperetl/models

YAML:

    python -m paperetl.file /data/paperetl/data yaml:///data/paperetl/yaml /data/paperetl/models

Converted files will be stored in /data/paperetl
