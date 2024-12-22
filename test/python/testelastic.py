"""
Elastic tests
"""

import unittest

from unittest import mock

from paperetl.elastic import Elastic
from paperetl.schema.article import Article


class Indices:
    """
    Mock elasticsearch class for testing
    """

    # pylint: disable=C3001
    exists = lambda *args, **kwargs: True
    delete = lambda *args, **kwargs: True
    refresh = lambda *args, **kwargs: True


class ElasticStub:
    """
    Mock elasticsearch class for testing
    """

    # pylint: disable=C3001
    indices = Indices()
    bulk = lambda *args: True


class TestElastic(unittest.TestCase):
    """
    Elastic tests
    """

    @mock.patch("paperetl.elastic.Elasticsearch", mock.MagicMock(return_value=ElasticStub()))
    @mock.patch("paperetl.elastic.helpers", mock.MagicMock(return_value=ElasticStub()))
    def testSave(self):
        """
        Tests saving an article to elasticsearch
        """

        # Create connection
        elastic = Elastic("http://localhost:9200", False)

        # Save mock results
        for _ in range(1000):
            elastic.save(Article(Article.ARTICLE, [("name", "text")]))

        # Mark as complete
        elastic.complete()
