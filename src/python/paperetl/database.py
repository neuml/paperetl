"""
Database module
"""

class Database(object):
    """
    Defines data structures and methods to store article content.
    """

    # pylint: disable=W0613
    def merge(self, url, ids):
        """
        Merges the results of an existing database into the current database. This method returns
        a list of ids not merged, which means there is a newer version available in the source data.

        Args:
            url: database connection
            ids: dict of id - entry date

        Returns:
            list of eligible ids NOT merged
        """

        return []

    def save(self, article):
        """
        Saves an article.

        Args:
            article: article metadata and text content
        """

    def complete(self):
        """
        Signals processing is complete and runs final storage methods.
        """

    def close(self):
        """
        Commits and closes the database.
        """
