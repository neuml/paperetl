"""
File ETL to database tests
"""

import sqlite3

from paperetl.file.execute import Execute

# pylint: disable = C0411
from testprocess import TestProcess
from utils import Utils


class TestFileDatabase(TestProcess):
    """
    File ETL to database tests
    """

    @classmethod
    def setUpClass(cls):
        """
        One-time initialization. Run File ETL process for the test dataset.
        """

        # Build articles database
        Execute.run(Utils.FILE + "/data", Utils.FILE + "/models")

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

        self.articleCount(17)

    def testArticles(self):
        """
        Test article metadata
        """

        hashes = {
            "00398e4c637f5e5447e35e63669187f0239c0357": "e4bab29931654fbf2569fe88c9947138",
            "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "8a9deb80f42173aa0681d7607925c63b",
            "1000": "babc1842c2dd9bf298bf6376a1b58318",
            "1001": "d8579348f06c6428565cab60ef797d0d",
            "17a845a8681cca77a4497462e797172148448d7d": "8b5e4696e66934afe75e1d9d14aeb445",
            "1d6a755d67e76049551898de66c95f77b9420b0c": "b1cac46801d2dd58ec2df9ce14986af2",
            "33024096": "c6d63a5a2761519f31cff6f690b9f639",
            "33046957": "62634d987e1d5077f9892a059fec8302",
            "33100476": "ba7c2509e242b2132d32baa48a1dc2ed",
            "33126180": "d8fe2cb1d95ddf74d79e6a5e2c58bd07",
            "33268238": "3f0f851d08c0138d9946db1641a5278e",
            "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "3facd9a50cf7a0e038ed0e6b3903a8b0",
            "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "3251a20e067e1bd5291e56e9cb20218e",
            "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "d14bebf4a6f4103498b02b5604649619",
            "a09f0fcf41e01f2cdb5685b5000964797f679132": "ef24259c459d09612d0e6d4430b3e8bd",
            "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "60bb318db90bfb305b2343c54242d689",
            "dff0088d65a56e2673d11ad2f7a180687cab6f70": "4fc1512bbceb439fd4ff4a7132b08735",
        }

        self.articles(hashes)

    def testSectionCount(self):
        """
        Test number of sections
        """

        self.sectionCount(3646)

    def testSections(self):
        """
        Test section content
        """

        hashes = {
            "00398e4c637f5e5447e35e63669187f0239c0357": "cd5548d4c6dc551429b9544edfc1d40a",
            "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "fe8778439a5aa68fe48f0bfbcc48d021",
            "1000": "2a2708e0a5e9847955bb7b441a4f7ea4",
            "1001": "147aca4eade4737a7a1d438a5a1d3ed1",
            "17a845a8681cca77a4497462e797172148448d7d": "8c50748e74883ac316d2473cf491d4e0",
            "1d6a755d67e76049551898de66c95f77b9420b0c": "799d21a7c67b5b4777effb2c83a42ff4",
            "33024096": "485b6035e1cd62e5ded8c356acc5689f",
            "33046957": "1e7833214fc60b89316f3680e9f93ec1",
            "33100476": "a5db58cd71ba75e76fa8df24e3336db6",
            "33126180": "e9d4cf8db964421780ff8e2946461980",
            "33268238": "1077e7a114d54bdf80de5d6834fdeb63",
            "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "1fc2ccc509b2bd7eca33858c740e54c2",
            "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "e2e28cb740520bae95acd373a6c767a9",
            "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "2387f11ea786cc4265c54f096080ad00",
            "a09f0fcf41e01f2cdb5685b5000964797f679132": "78596af571f3250057c1df23eabfc498",
            "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "51d5b0cf2273a687a348502c95c6dbec",
            "dff0088d65a56e2673d11ad2f7a180687cab6f70": "c61df238a8ecb9a63422f19b2218949d",
        }

        self.sections(hashes)
