"""
Study analysis test module
"""

import csv
import os
import sqlite3
import unittest

import spacy

# pylint: disable=E0401
from paperetl.file.execute import Execute
from paperetl.study.attribute import Attribute
from paperetl.study.design import Design

from utils import Utils

class TestStudy(unittest.TestCase):
    """
    Study analysis tests
    """

    def setUp(self):
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
