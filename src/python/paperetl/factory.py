"""
Factory module
"""

from .elastic import Elastic
from .jsonw import JSON
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

        if url.startswith("http://"):
            return Elastic(url)
        elif url.startswith("json://"):
            return JSON(url.replace("json://", ""))
        elif url:
            # If URL is present, assume it's SQLite
            return SQLite(url.replace("sqlite://", ""))

        return None
