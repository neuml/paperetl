"""
Article module.
"""

class Article(object):
    """
    Article objects. Holds all metadata and text content related to an article.
    """

    # Articles schema
    ARTICLE = ("id", "source", "published", "publication", "authors", "title", "tags", "design",
               "size", "sample", "method", "reference", "entry")

    # Sections schema
    SECTION = ("name", "text", "labels")

    def __init__(self, metadata, sections, source):
        """
        Stores article metadata and section content as an object.

        Args:
            metadata: article metadata
            sections: text sections
            source: article source
        """

        self.metadata = metadata
        self.sections = sections
        self.source = source

    def uid(self):
        """
        Returns the article uid.

        Returns:
            article uid
        """

        return self.metadata[0]

    def tags(self):
        """
        Returns the article tags.

        Returns:
            article tags
        """

        return self.metadata[6]

    def design(self):
        """
        Returns the article design.

        Returns:
            article design
        """

        return self.metadata[7]

    def build(self):
        """
        Builds an article with all metadata and section content.

        Returns:
            object with full article content
        """

        # Create article
        article = dict(zip(Article.ARTICLE, self.metadata))

        # Create sections
        sections = [dict(zip(Article.SECTION, section)) for section in self.sections]

        # Add sections to article
        article["sections"] = sections

        return article
