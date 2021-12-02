"""
Text module
"""

import re

# Compiled pattern for cleaning text
# pylint: disable=W0603
PATTERN = None


def getPattern():
    """
    Gets or builds a pre-compiled regex for cleaning text.

    Returns:
        compiled regex
    """

    global PATTERN

    if not PATTERN:
        # List of patterns
        patterns = []

        # Remove emails
        patterns.append(r"\w+@\w+(\.[a-z]{2,})+")

        # Remove urls
        patterns.append(r"http(s)?\:\/\/\S+")

        # Remove single characters repeated at least 3 times (ex. j o u r n a l)
        patterns.append(r"(^|\s)(\w\s+){3,}")

        # Remove citations references (ex. [3] [4] [5])
        patterns.append(r"(\[\d+\]\,?\s?){3,}(\.|\,)?")

        # Remove citations references (ex. [3, 4, 5])
        patterns.append(r"\[[\d\,\s]+\]")

        # Remove citations references (ex. (NUM1) repeated at least 3 times with whitespace
        patterns.append(r"(\(\d+\)\s){3,}")

        PATTERN = re.compile("|".join([f"({p})" for p in patterns]))

    return PATTERN


class Text:
    """
    Methods for formatting and cleaning text.
    """

    @staticmethod
    def transform(text):
        """
        Transforms and cleans text to help improve text indexing accuracy.

        Args:
            text: input text line

        Returns:
            transformed text
        """

        # Clean/transform text
        text = getPattern().sub(" ", text)

        # Remove extra spacing either caused by replacements or already in text
        text = re.sub(r" {2,}|\.{2,}", " ", text)

        return text
