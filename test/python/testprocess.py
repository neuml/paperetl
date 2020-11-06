"""
Generic ETL process test module
"""

import unittest

from utils import Utils

class TestProcess(unittest.TestCase):
    """
    Generic ETL process test
    """

    # Database connection
    db, cur = None, None

    def articleCount(self, count):
        """
        Test number of articles.

        Args:
            count: expected count
        """

        self.cur.execute("SELECT COUNT(*) FROM articles")
        self.assertEqual(self.cur.fetchone()[0], count)

    def articles(self, hashes):
        """
        Test article metadata.

        Args:
            hashes: expected hashes
        """

        self.cur.execute("SELECT * FROM articles ORDER BY id")
        for row in self.cur.fetchall():
            # Calculate row hash
            md5 = Utils.hashtext(" ".join([str(x) for x in row]))

            # Check hash equals expected value
            self.assertEqual(hashes[row[0]], md5)

    def sectionCount(self, count):
        """
        Test number of sections.

        Args:
            count: expected count
        """

        self.cur.execute("SELECT COUNT(*) FROM sections")
        self.assertEqual(self.cur.fetchone()[0], count)

    def sections(self, hashes):
        """
        Test section content.

        Args:
            hashes: expected hashes
        """

        self.cur.execute("SELECT id FROM articles ORDER BY id")
        for row in self.cur.fetchall():
            # Get list of sections
            self.cur.execute("SELECT * FROM sections WHERE article = ? ORDER BY id", [row[0]])

            text = [str(y) for x in self.cur.fetchall() for y in x]
            md5 = Utils.hashtext(" ".join(text))

            # Check hash equals expected value
            self.assertEqual(hashes[row[0]], md5)
 