"""
Factory module
"""

from .elastic import Elastic
from .filesystem import JSON, YAML
from .sqlite import SQLite


class Factory:
    """
    Database Factory - creates database connections
    """

    @staticmethod
    def create(url, replace):
        """
        Creates a new database connection.

        Args:
            url: connection url
            replace: if true, a new database will be created, overwriting any existing database

        Returns:
            Database
        """

        if url.startswith("http://"):
            return Elastic(url, replace)
        if url.startswith("json://"):
            return JSON(url.replace("json://", ""))
        if url.startswith("yaml://"):
            return YAML(url.replace("yaml://", ""))
        if url:
            # If URL is present, assume it's SQLite
            return SQLite(url.replace("sqlite://", ""), replace)

        return None
