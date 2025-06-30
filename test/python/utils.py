"""
Utils module
"""

import hashlib


class Utils:
    """
    Utility constants and methods
    """

    PATH = "/tmp/paperetl"
    DATA = PATH + "/data"
    MODELS = PATH + "/models"

    @staticmethod
    def hashtext(text):
        """
        Builds a MD5 hash for input text.

        Args:
            text: input text

        Returns:
            MD5 hash
        """

        return hashlib.md5(text.encode()).hexdigest()
