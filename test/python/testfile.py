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

        hashes = {"00398e4c637f5e5447e35e63669187f0239c0357": "bef1d093d75c0b867c6c0ecd679f0987",
                  "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "9bfb614f0ea91f43e5fb92c0025ee0e8",
                  "17a845a8681cca77a4497462e797172148448d7d": "1539f4740300d15596e9c04df505ed57",
                  "1d6a755d67e76049551898de66c95f77b9420b0c": "7a3efeb9229751a4febc6eed7b48faf4",
                  "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "6721860a1deb25a7dd71992add19392f",
                  "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "5a6c7ce6811038fc774c9a8e771243d5",
                  "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "e3d0f190d503aab89045c82e127e593c",
                  "a09f0fcf41e01f2cdb5685b5000964797f679132": "fc754a4a00e82ad4f01194556e4f5a11",
                  "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "5415730597346d60d73d3f993c0b82e9",
                  "dff0088d65a56e2673d11ad2f7a180687cab6f70": "68353f688a200e51cd656dc4a7c9b349"}

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

        hashes = {"00398e4c637f5e5447e35e63669187f0239c0357": "d6e428814a980bdbed5f50b2669f6785",
                  "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "cfd8bf5cffec86b836e497ac4973ea05",
                  "17a845a8681cca77a4497462e797172148448d7d": "422895ced816b2686ed4ea34c62e0f3a",
                  "1d6a755d67e76049551898de66c95f77b9420b0c": "644e14e17727715a205f1f92a5d98d83",
                  "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "a3429b2fce7efa296282cf8923a37fe6",
                  "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "4ec8a19839db5adf64c50b250d8c1081",
                  "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "d9f536cbca1abaab53682423d0b51af5",
                  "a09f0fcf41e01f2cdb5685b5000964797f679132": "f04bb10cd15dea0180e9ae610a8ada9a",
                  "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "79581ee4ec2f6b6339afba4df559c927",
                  "dff0088d65a56e2673d11ad2f7a180687cab6f70": "d214010dbae4fff941875b4dfe57ee71"}

        self.sections(hashes)
