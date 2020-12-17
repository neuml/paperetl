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

        hashes = {"1ycj3b66": "a4f3d1219b1fa0be80de2792c7f97d48",
                  "2xoczdmh": "ff2fb178a73d567bd01d4281c9dac411",
                  "4jri92pu": "9aa014e20ab20191919156ceafb9a8a8",
                  "7u3d6nfc": "50703188014aaadb5f0155c5fbfa4abd",
                  "c6nq7nli": "65ef47241aaa62c8b7896d114b0c4658",
                  "cx2h5bsw": "98f8c1c37ca25ef2a8cc121fc8a8502e",
                  "lnzz2chk": "7ecd68424d1ff7cd53ca8ae2fa80a56c",
                  "mb0qcd0b": "ca4c2f9ceff89c0e63bb933cc7bb5cd4",
                  "qg1ahdx5": "ee97b9304a3dc7209392464f565d5037",
                  "uqkiglu3": "70e5575be41cbde2c7b42edc29a454b3"}

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
