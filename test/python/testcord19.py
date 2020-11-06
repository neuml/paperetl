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

        hashes = {"1ycj3b66": "ecb4b2f46b10b3a55854c13feb86bc32",
                  "2xoczdmh": "1daef2ac414a5be9b195527e973472ac",
                  "4jri92pu": "8fe14c25c1eda20cc808005c1148c472",
                  "7u3d6nfc": "5fabe638bb5d9fcac1b329c494094dc8",
                  "c6nq7nli": "05e72d710f6b108e9b789420e74ad84d",
                  "cx2h5bsw": "641beb59ffcd3107ff5b9341a4e0f115",
                  "lnzz2chk": "525b5350f8e1b8d67629fd4ebc8733ff",
                  "mb0qcd0b": "e791208181dda9cd650f52f08512a6fa",
                  "qg1ahdx5": "4fb661d30ff973d1c939ea6eb0a374da",
                  "uqkiglu3": "0b6780efa797908d9a10999853e579c8"}

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

        hashes = {"1ycj3b66": "1ef11c012cec152fb92ad7116f16f73a",
                  "2xoczdmh": "477bec44cbaeb545b4612934b769bbe0",
                  "4jri92pu": "a4595820598444f82b7ae4eaab63f1a3",
                  "7u3d6nfc": "ca54708fc11dfcd383116307d4bd9806",
                  "c6nq7nli": "7fe5856da9211f1030a1d8768d0d7c25",
                  "cx2h5bsw": "f22d3a4f2ddb2f3b2043c5c8cc7d4053",
                  "lnzz2chk": "9d727c131a46eed29fea5653fc646a7f",
                  "mb0qcd0b": "648ca163cd3006197a4683396e581584",
                  "qg1ahdx5": "bbdd07f6171c40d161e21a52baacc3d0",
                  "uqkiglu3": "daf55a623de742f6739a85993d3a0f9b"}

        self.sections(hashes)
