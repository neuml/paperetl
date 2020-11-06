"""
CORD-19 tests
"""

import sqlite3

# pylint: disable=E0401
from paperetl.cord19.execute import Execute

from testprocess import TestProcess
from utils import Utils

class TestCord19(TestProcess):
    """
    CORD-19 tests
    """

    @classmethod
    def setUpClass(cls):
        """
        One-time initialization. Run CORD-19 ETL process for the test dataset.
        """

        # Build articles database
        Execute.run(Utils.CORD19 + "/data", Utils.CORD19 + "/models", Utils.PATH + "/study", Utils.CORD19 + "/data/entry-dates.csv", True, None)

    def setUp(self):
        """
        Initialization run before each test. Opens a database connection.
        """

        # Connect to articles database
        self.db = sqlite3.connect(Utils.CORD19 + "/models/articles.sqlite")

        # Create database cursor
        self.cur = self.db.cursor()

    def testArticleCount(self):
        """
        Test number of articles
        """

        self.articleCount(10)

    def testArticles(self):
        """
        Test article metadata
        """

        hashes = {"1ycj3b66": "2be5995ae9fbda2130cba228beb1793e",
                  "2xoczdmh": "4745da2b79c0cfc40f24c368bc704ecd",
                  "4jri92pu": "df8f6983d038445e989eb38ff12acf5d",
                  "7u3d6nfc": "256187676ee132e311d2ce59bc3cc482",
                  "c6nq7nli": "c77167dbc56c7be04b1cafcba759947d",
                  "cx2h5bsw": "f669332a538979eac50d7d16214b78ef",
                  "lnzz2chk": "4267ee7c03ed3799439c938f925b573d",
                  "mb0qcd0b": "d218d2d0b620195c5fe709879c382b3a",
                  "qg1ahdx5": "e52c38ca367505f02caba8bb46134aec",
                  "uqkiglu3": "f5e914413ff4e507eff597e5a91b7c3a"}

        self.articles(hashes)

    def testSectionCount(self):
        """
        Test number of sections
        """

        self.sectionCount(3789)

    def testSections(self):
        """
        Test section content
        """

        hashes = {"1ycj3b66": "47cb6c1c32944d4c0684e1cfa6ddecb5",
                  "2xoczdmh": "799e2149576867cfa5bab455de49e7e5",
                  "4jri92pu": "2e277dd7caa4890db6bbadb0e72c1ccd",
                  "7u3d6nfc": "6ef19b5e30551d1e7f7f08131bcd5fcc",
                  "c6nq7nli": "08c18b8a901027fe8a634e6413a55eca",
                  "cx2h5bsw": "2b0ec3ef1a07f77e59e144ffb770d8c9",
                  "lnzz2chk": "49fcdf4be0165a54dda3f2b06d7915f3",
                  "mb0qcd0b": "ee068155e2ee92265790da17028ff748",
                  "qg1ahdx5": "006dea0aa9c97c5e71b06c4327addfbe",
                  "uqkiglu3": "906a4fdd639c942e7c05192f3f48e302"}

        self.sections(hashes)
