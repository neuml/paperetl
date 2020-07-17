"""
Database module
"""

class Database(object):
    """
    Defines data structures and methods to store article content.
    """

    def save(self, article):
        """
        Saves an article.

        Args:
            article: article metadata and text content
        """

    def complete(self, citations):
        """
        Signals processing is complete and runs final storage methods.

        Args:
            citations: all citations found
        """

    def close(self):
        """
        Commits and closes the database.
        """
