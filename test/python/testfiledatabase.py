"""
File ETL to database tests
"""

import sqlite3

from unittest import mock

from paperetl.file.execute import Execute
from paperetl.file.pdf import PDF

# pylint: disable = C0411
from testprocess import TestProcess
from utils import Utils


class RequestsStub:
    """
    Mock requests class for testing.
    """

    def __init__(self):
        self.ok = True
        with open(Utils.FILE + "/data/0.xml", "r", encoding="utf-8") as xml:
            self.text = xml.read()


class TestFileDatabase(TestProcess):
    """
    File ETL to database tests
    """

    @classmethod
    def setUpClass(cls):
        """
        One-time initialization. Run file ETL process for the test dataset.
        """

        # Build articles database
        Execute.run(Utils.FILE + "/data", Utils.FILE + "/models", None, True)

        # Run again with replace=False
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

        self.articleCount(20)

    def testArticles(self):
        """
        Test article metadata
        """

        hashes = {
            "00398e4c637f5e5447e35e63669187f0239c0357": "769aabf322421b2e34a32d7afce4d046",
            "00c4c8c42473d25ebb38c4a8a14200c6900be2e9": "c1b8cebfb55231215a865eaa8e16d338",
            "1000": "babc1842c2dd9bf298bf6376a1b58318",
            "1001": "d8579348f06c6428565cab60ef797d0d",
            "17a845a8681cca77a4497462e797172148448d7d": "f1768e230244ab984530c482f275f439",
            "1d6a755d67e76049551898de66c95f77b9420b0c": "a239023786db03a0bc7ae00780c396df",
            "3a1e7ec128ae12937badcd33f2a273b284714550": "37f1dd1e15347ae325aa09901d1767f3",
            "33024096": "c6d63a5a2761519f31cff6f690b9f639",
            "33046957": "62634d987e1d5077f9892a059fec8302",
            "33100476": "ba7c2509e242b2132d32baa48a1dc2ed",
            "33126180": "d8fe2cb1d95ddf74d79e6a5e2c58bd07",
            "33268238": "3f0f851d08c0138d9946db1641a5278e",
            "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "6920b2807d6955a8b2fefd5b0a59219e",
            "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "26a92c9d288412e73476c3c1f3107e20",
            "68d85e38ab25365d8a382b146305aa8560bfa6fa": "e45f785edc439dfea64b6ff929fa9b44",
            "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "53ff57038e6257a5fa8032cdc40b0750",
            "a09f0fcf41e01f2cdb5685b5000964797f679132": "d2a98edeb923ec781a44bf7c166bfc77",
            "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "a7b77a4e68f9134e134c306b00d489d8",
            "da60cb944e50dbecbfd217581cb5f55bda332d7a": "a39676892934b50d7cd2e299f3a68d21",
            "dff0088d65a56e2673d11ad2f7a180687cab6f70": "f22696dbdce156d5a81b7231d1ef983b",
        }

        self.articles(hashes)

    @mock.patch(
        "paperetl.file.pdf.requests.post", mock.MagicMock(return_value=RequestsStub())
    )
    def testPDF(self):
        """
        Tests parsing PDFs
        """

        article = PDF.parse("stream", "source")

        # Calculate metadata hash
        md5 = Utils.hashtext(" ".join([str(x) for x in article.metadata[:-1]]))

        self.assertEqual(md5, "0e04572de9c87fdbdc5339b03aee1df9")
        self.assertEqual(len(article.sections), 254)

    def testSectionCount(self):
        """
        Test number of sections
        """

        self.sectionCount(3668)

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
            "3a1e7ec128ae12937badcd33f2a273b284714550": "2a0e6610a4edce73005ddaf740117aee",
            "33024096": "485b6035e1cd62e5ded8c356acc5689f",
            "33046957": "1e7833214fc60b89316f3680e9f93ec1",
            "33100476": "a5db58cd71ba75e76fa8df24e3336db6",
            "33126180": "e9d4cf8db964421780ff8e2946461980",
            "33268238": "1077e7a114d54bdf80de5d6834fdeb63",
            "3d2fb136bbd9bd95f86fc49bdcf5ad08ada6913b": "1fc2ccc509b2bd7eca33858c740e54c2",
            "5ea7c57e339a078196ec69223c4681fd7a5aab8b": "e2e28cb740520bae95acd373a6c767a9",
            "68d85e38ab25365d8a382b146305aa8560bfa6fa": "9772fa38bdafd56dc1599ce02ff10c1e",
            "6cb7a79749913fa0c2c3748cbfee2f654d5cea36": "2387f11ea786cc4265c54f096080ad00",
            "a09f0fcf41e01f2cdb5685b5000964797f679132": "78596af571f3250057c1df23eabfc498",
            "b9f6e3d2dd7d18902ac3a538789d836793dd48b2": "51d5b0cf2273a687a348502c95c6dbec",
            "da60cb944e50dbecbfd217581cb5f55bda332d7a": "73f7744629e4feb5988acbd31117c7f1",
            "dff0088d65a56e2673d11ad2f7a180687cab6f70": "c61df238a8ecb9a63422f19b2218949d",
        }

        self.sections(hashes)
