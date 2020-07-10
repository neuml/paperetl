"""
Database module
"""

class Database(object):
    """
    Defines data structures and methods to store article content.
    """

    def save(self, uid, article, sections, tags, design):
        """
        Saves an article.

        Args:
            uid: unique id
            article: article metadata
            section: list of sections
            tags: list of tags
            design: study design
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
