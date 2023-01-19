"""
Elasticsearch module
"""

from elasticsearch import Elasticsearch, helpers

from .database import Database


class Elastic(Database):
    """
    Defines data structures and methods to store article content in Elasticsearch.
    """

    # Articles index
    ARTICLES = {
        "settings": {
            "number_of_shards": 5,
            "number_of_replicas": 0,
            "index.mapping.nested_objects.limit": 30000,
        },
        "mappings": {"properties": {"sections": {"type": "nested"}}},
    }

    def __init__(self, url, replace):
        """
        Connects and initializes an elasticsearch instance.

        Args:
            url: elasticsearch url
            replace: If database should be recreated
        """

        # Connect to ES instance
        self.connection = Elasticsearch(hosts=[url], timeout=60, retry_on_timeout=True)

        # Row count
        self.rows = 0

        # Buffered actions
        self.buffer = []

        # Check if index exists
        exists = self.connection.indices.exists(index="articles")

        # Delete if replace enabled
        if exists and replace:
            self.connection.indices.delete(index="articles")
            exists = False

        # Create if necessary
        if not exists:
            self.connection.indices.create(
                index="articles",
                settings=Elastic.ARTICLES["settings"],
                mappings=Elastic.ARTICLES["mappings"],
            )

    def save(self, article):
        # Build article
        article = article.build()

        # Bulk action fields
        article["_id"] = article["id"]
        article["_index"] = "articles"

        # Buffer article
        self.buffer.append(article)

        # Increment number of articles processed
        self.rows += 1

        # Bulk load every 1000 records
        if self.rows % 1000 == 0:
            helpers.bulk(self.connection, self.buffer)
            self.buffer = []

            print(f"Inserted {self.rows} articles", end="\r")

    def complete(self):
        # Load remaining buffered articles
        if self.buffer:
            helpers.bulk(self.connection, self.buffer)

        print(f"Total articles inserted: {self.rows}")

        # Refresh indices
        self.connection.indices.refresh(index="articles")

    def close(self):
        self.connection.close()
