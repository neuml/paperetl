"""
CORD-19 tests
"""

import sqlite3

from datetime import datetime

from paperetl.cord19.entry import Entry
from paperetl.cord19.execute import Execute

# pylint: disable = C0411
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
        Execute.run(
            Utils.CORD19 + "/data",
            Utils.CORD19 + "/models",
            Utils.CORD19 + "/data/entry-dates.csv",
            True,
        )

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

        hashes = {
            "1ycj3b66": "27c9aa8532e999788bc2922e55b48dfe",
            "2xoczdmh": "d19f72095f4c807d9e35d7eb68884191",
            "4jri92pu": "a725e6ef67d9e19659fc6dc3606b502c",
            "7u3d6nfc": "2b72b90ab209d44310ac8eb493defe50",
            "c6nq7nli": "c39fded39444dc039b6a7c626a329331",
            "cx2h5bsw": "99ddefc96814e698da796f0f1e76a8a2",
            "lnzz2chk": "436cc401bdf84e64c9184030a43f24ec",
            "mb0qcd0b": "38f610c6a0e1d35f2d66e72bc71defa0",
            "qg1ahdx5": "17b6e5545f3c860e57ca586044465f13",
            "uqkiglu3": "9474fa794b9fc9062bcd0ffa3eeefa10",
        }

        self.articles(hashes)

    def testDate(self):
        """
        Test article publish dates
        """

        self.assertEqual(Execute.getDate({"publish_time": "2020"}), datetime(2020, 1, 1))
        self.assertEqual(Execute.getDate({"publish_time": "2020-10-10"}), datetime(2020, 10, 10))
        self.assertEqual(Execute.getDate({"publish_time": "bad date"}), None)
        self.assertEqual(Execute.getDate({"publish_time": None}), None)

    def testEntryDates(self):
        """
        Test entry date file generation
        """

        Entry.run(Utils.PATH, "2020-03-27")

        # Validate line count
        count = 0
        with open(Utils.PATH + "/entry-dates.csv", encoding="utf-8") as f:
            count = sum(1 for x in f)

        self.assertEqual(count, 45351)

    def testHash(self):
        """
        Test article sha hashes
        """

        self.assertEqual(
            Execute.getHash({"sha": "47ed55bfa014cd59f58896c132c36bb0a218d11d"}),
            "47ed55bfa014cd59f58896c132c36bb0a218d11d",
        )
        self.assertEqual(
            Execute.getHash({"sha": None, "title": "Test title"}),
            "62520f1c4f656dcb5fe565a4c2bf4ce1f7d435ef",
        )
        self.assertEqual(
            Execute.getHash({"sha": "47ed55bfa014cd59f58896c132c36bb0a218d11d; abcdef"}),
            "47ed55bfa014cd59f58896c132c36bb0a218d11d",
        )

    def testSectionCount(self):
        """
        Test number of sections
        """

        self.sectionCount(3789)

    def testSections(self):
        """
        Test section content
        """

        hashes = {
            "1ycj3b66": "9acb529ca75cf0143c6dce529b89376d",
            "2xoczdmh": "dee1b2a0d4478a80085b3ec359694f17",
            "4jri92pu": "ce161da9327cafbca4d51ee73e4d64d2",
            "7u3d6nfc": "cc4faa2154572f38b6df7cd18bf44fb7",
            "c6nq7nli": "4964861f7852de0bc1347ee6d269d109",
            "cx2h5bsw": "7429fb1c349c4a3e5df27a86745d74be",
            "lnzz2chk": "99d3e26d511dc4c80416c86507cb8bb4",
            "mb0qcd0b": "0f22f69902598bb9459150e3ebb35fea",
            "qg1ahdx5": "96c0b5a23345d875eebc13ed78cdf7c2",
            "uqkiglu3": "d250a22436e0a806f624a720e90ade5f",
        }

        self.sections(hashes)
