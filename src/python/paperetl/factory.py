"""
Factory module
"""

from .elastic import Elastic
from .sqlite import SQLite

class Factory(object):
    """
    Database Factory - creates database connections
    """

    @staticmethod
    def create(url):
        """
        Creates a new database connection.

        Args:
            url: connection url

        Returns:
            Database
        """

        return Elastic(url) if url.startswith("http://") else SQLite(url)
