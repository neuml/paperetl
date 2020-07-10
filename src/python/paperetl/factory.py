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
    def create(backend, args):
        """
        Creates a new database connection.

        Args:
            backend: database type
            args: database arguments

        Returns:
            Database
        """

        if backend == "elasticsearch":
            return Elastic(*args)
        elif backend == "sqlite":
            return SQLite(*args)

        return None
