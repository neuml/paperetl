"""
Study analysis test module
"""

import csv
import os
import sqlite3
import unittest

import spacy

# pylint: disable=E0401
from paperetl.grammar import Grammar
from paperetl.file.execute import Execute
from paperetl.study.attribute import Attribute
from paperetl.study.design import Design
from paperetl.study.sample import Sample
from paperetl.study.vocab import Vocab

from utils import Utils

class TestStudy(unittest.TestCase):
    """
    Study analysis tests
    """

    def setUp2(self):
        """
        Initialization run before each test. Opens a database connection.
        """

        dbfile = Utils.FILE + "/models/articles.sqlite"

        # Build articles database if it doesn't exist
        if not os.path.exists(dbfile):
            Execute.run(Utils.FILE + "/data", Utils.FILE + "/models", Utils.STUDY)

        # Connect to articles database
        self.dbfile = Utils.FILE + "/models/articles.sqlite"
        self.db = sqlite3.connect(self.dbfile)

        # Create database cursor
        self.cur = self.db.cursor()

        # Training directory
        self.directory = Utils.STUDY + "/training"
        os.makedirs(self.directory, exist_ok=True)

    def testAttribute(self):
        """
        Tests building an attribute model
        """

        # Use data in database as training data
        statements = ["SELECT 0, text FROM sections WHERE labels IS NULL ORDER BY id LIMIT 50",
                      "SELECT 1, text FROM sections WHERE labels='STATISTIC' ORDER BY id LIMIT 25",
                      "SELECT 2, text FROM sections WHERE labels='SAMPLE_METHOD' ORDER BY id LIMIT 25",
                      "SELECT 3, text FROM sections WHERE labels='SAMPLE_SIZE' ORDER BY id LIMIT 25"]

        # Training file
        training = self.directory + "/attribute.csv"
        model = self.directory + "/attribute"

        # Select and write rows to training csv
        with open(training, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["label", "text"])

            for statement in statements:
                for row in self.cur.execute(statement).fetchall():
                    writer.writerow(row)

        # Train the model
        Attribute.run(training, self.directory, {"cv": 2, "verbose": 0}, False)

        # Test loading model
        attribute = Attribute()
        attribute.load(model)

        # Load NLP model to parse tokens
        nlp = spacy.load("en_core_sci_md")

        # Test prediction
        row = (None, "This is a test", nlp("This is a test"))
        self.assertIsNotNone(attribute.predict([row]))

    def testDesign(self):
        """
        Tests building a design model
        """

        # Training file
        training = self.directory + "/design.csv"
        model = self.directory + "/design"

        # Select and write rows to training csv
        with open(training, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["label", "id"])

            for row in self.cur.execute("SELECT design, id FROM articles ORDER BY design, id").fetchall():
                writer.writerow(row)

        # Train the model
        Design.run(training, self.dbfile, {"cv": 2, "verbose": 0}, False)

        # Test loading model
        design = Design()
        design.load(model)

        # Test prediction
        row = (None, "This is a test", "This is a test".split())
        self.assertIsNotNone(design.predict([row]))

    def testSample(self):
        """
        Test sample size extraction
        """

        samples = ["One hundred fifty-two eligible patients were treated",
                   "One hundred fifty two eligible patients were treated",
                   "52000 eligible patients were treated",
                   "52,000 eligible patients were treated",
                   "37 studies were used with 85 patients",
                   "Three patients were enrolled",
                   "Of 10 224 admitted patients",
                   "The 16 studies had 3,4 and 5 patients respectively",
                   "Out of the twenty five hundred total patients 33 were enrolled",
                   "Though only 54 cases have been reported to our knowledge",
                   "Data from 33 560 adults at 10 centers"]

        # Parse samples into NLP tokens
        grammar = Grammar()
        tokenlist = grammar.parse(samples)

        # Extract sample sizes and validate
        sizes = [Sample.find(tokens, Vocab.SAMPLE) for tokens in tokenlist]
        self.assertEqual(sizes, ["152", "152", "52000", "52000", "37", "3", "10224", "16", "2500", "54", "33560"])