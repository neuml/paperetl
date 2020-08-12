# paperetl: ETL processes for medical and scientific papers

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

Download the latest dataset on the [Allen Institute for AI CORD-19 Release Page](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html). Go to the directory with the file and run the following commands.

    cd <download_path>
    tar -xvzf cord-19_$DATE.tar.gz

Where $DATE is the yyyy-mm-dd formatted date string in the file downloaded. Once completed, there should be a file named metadata.csv and subdirectories with all json articles.

Build the database:

    # Download pre-trained study design/attribute models
    # https://www.kaggle.com/davidmezzetti/cord19-study-design/#attribute
    # https://www.kaggle.com/davidmezzetti/cord19-study-design/#design
    # Default location: ~/.cord19/models/attribute, ~/.cord19/models/design

    # Download entry-dates.csv and place in <download path>
    # https://www.kaggle.com/davidmezzetti/cord-19-article-entry-dates/output

    # Execute the ETL process to load articles into SQLite
    python -m paperetl.cord19 <download_path>

Once complete, there will be an articles.sqlite file in ~/.cord19/models

### Load PDF Articles into SQLite
The following example shows how to use paperetl to load a set of medical/scientific pdf articles into a SQLite database.

Download the desired medical/scientific articles in a local directory. For this example, it is assumed the articles are in a directory named /data/scipaper/

Build the database:

    # Download pre-trained study design/attribute models
    # https://www.kaggle.com/davidmezzetti/cord19-study-design/#attribute
    # https://www.kaggle.com/davidmezzetti/cord19-study-design/#design
    # Default location: ~/.paperai/models/attribute, ~/.paperai/models/design

    # Load PDF articles into SQLite
    python -m paperetl.file /data/scipaper ~/.paperai/models ~/.paperai/models

Once complete, there will be an articles.sqlite file in ~/.paperai/models

### Load into Elasticsearch
Both of the examples above also support storing data in Elasticsearch with the following changes. These examples assume Elasticsearch is running locally, change the URL to a remote server as appropriate.

CORD-19:

    python -m paperetl.cord19 <download_path> http://localhost:9200

PDF Articles:

    python -m paperetl.file /scipaper/input http://localhost:9200 ~/.paperai/models

Once complete, there will be an articles index in elasticsearch with the metadata and full text stored.

### Convert PDF articles to JSON/YAML
paperetl can also be used to convert PDF articles into JSON or YAML files. This is useful if the data is to be fed into another system or for manual inspection/debugging of a single file.

JSON:

    python -m paperetl.file /data/scipaper json:///data/scipaper ~/.paperai/models

YAML:

    python -m paperetl.file /data/scipaper yaml:///data/scipaper ~/.paperai/models

Converted files will be stored in /data/scipaper
