"""
Citation module.
"""

class Citation(object):
    """
    Citation objects. Holds all citation fields.
    """

    # Citations schema
    CITATION = ("title", "mentions")

    def __init__(self, values):
        """
        Stores citation content.

        Args:
            values: citation values
        """

        self.values = values

    def build(self):
        """
        Builds a full citation.

        Returns:
            citation
        """

        return dict(zip(Citation.CITATION, self.values))
