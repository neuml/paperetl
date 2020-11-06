"""
File tests
"""

import sqlite3

# pylint: disable=E0401
from paperetl.file.execute import Execute

from testprocess import TestProcess
from utils import Utils

class TestFile(TestProcess):
    """
    File tests
    """

    @classmethod
    def setUpClass(cls):
        """
        One-time initialization. Run File ETL process for the test dataset.
        """

        # Build articles database
        Execute.run(Utils.FILE + "/data", Utils.FILE + "/models", Utils.PATH + "/study")

    def setUp(self):
        """
        Initialization run before each test. Opens a database connection.
        """

        # Connect to articles database
        self.db = sqlite3.connect(Utils.FILE + "/models/articles.sqlite")

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

        hashes = {"00398e4c637f5e5447e35e63669187f0239c0357": "e05fba21510405e9331d6f203e180561",
                  "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "edc71263b9df5ebee0b1975f2d631d69",
                  "17a845a8681cca77a4497462e797172148448d7d": "d8e7de662184b28bb66bb8b2921e0cb4",
                  "1d6a755d67e76049551898de66c95f77b9420b0c": "22556e50ae634c58f4bb4a0948335eb8",
                  "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "1760fad111328b6db9886ca368e32e40",
                  "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "6d7a4d95150c7074b76ac104e64eeb5f",
                  "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "0d4a34902e1f28b1623cd0716f9d5f89",
                  "a09f0fcf41e01f2cdb5685b5000964797f679132": "c699bcc0a56890b0f1a680dbab5d9bfc",
                  "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "c0bb731ba81f9e31d69be14e8bec8189",
                  "dff0088d65a56e2673d11ad2f7a180687cab6f70": "888fda7e47104d1c4046e33f984bd309"}

        self.articles(hashes)

    def testSectionCount(self):
        """
        Test number of sections
        """

        self.sectionCount(3592)

    def testSections(self):
        """
        Test section content
        """

        hashes = {"00398e4c637f5e5447e35e63669187f0239c0357": "fdefde421444621fea00329c8c889eae",
                  "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "c1b3095a153dec0bc0f7c4150c761725",
                  "17a845a8681cca77a4497462e797172148448d7d": "c0876908cae3e99f6c3a544460a2a083",
                  "1d6a755d67e76049551898de66c95f77b9420b0c": "8439f4aeb540a0934607b49cf6738241",
                  "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "7d68f9440e82c1fbe898d42d426029db",
                  "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "c8b2c50a09946f5da829993576ed93c2",
                  "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "b0836f936cb41c6390e1a09e4d6276db",
                  "a09f0fcf41e01f2cdb5685b5000964797f679132": "1eda6151062e487b09e0fb34fa7bd877",
                  "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "509d2d732ff30dc56ee76f6772fc363e",
                  "dff0088d65a56e2673d11ad2f7a180687cab6f70": "729f2dfadeec694c17c9054274975b66"}

        self.sections(hashes)
