"""
Design module

Labels definitions:

  1 - Systematic review
  2 - Randomized control trial
  3 - Non-randomized trial
  4 - Prospective observational
  5 - Time-to-event analysis
  6 - Retrospective observational
  7 - Cross-sectional
  8 - Case series
  9 - Modeling
  0 - Other
"""

import csv
import os
import sqlite3
import sys

from itertools import groupby

import regex as re

from sklearn.ensemble import RandomForestClassifier

from .study import StudyModel
from .vocab import Vocab

class Design(StudyModel):
    """
    Prediction model used to classify study designs.
    """

    def __init__(self):
        """
        Builds a new Design model.

        Args:
            training: path to training data
            models: path to models
        """

        super(Design, self).__init__()

        # Keywords to use as features
        self.keywords = StudyModel.getKeywords()

    def predict(self, sections):
        # Build features array for document
        features = [self.features(sections)]

        return int(self.model.predict(features)[0])

    def create(self):
        return RandomForestClassifier(n_estimators=129, max_depth=21, max_features=0.22, random_state=0)

    def hyperparams(self):
        return {"n_estimators": range(125, 150),
                "max_depth": range(20, 30),
                "max_features": [x / 100 for x in range(15, 25)],
                "random_state": (0,)}

    def data(self, training):
        # Unique ids
        uids = {}

        # Features
        ids = []
        features = []
        labels = []

        # Unpack training data
        training, db = training
        cur = db.cursor()

        # Read training data, convert to features
        with open(training, mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                uids[row["id"]] = int(row["label"])

            # Build id list for each uid batch
            for idlist in self.batch(list(uids.keys()), 999):
                # Get section text and transform to features
                cur.execute("SELECT name, text, article FROM sections WHERE article in (%s) ORDER BY id" % ",".join(["?"] * len(idlist)), idlist)
                i, f, l = self.transform(cur.fetchall(), uids)

                # Combine lists from each batch
                ids.extend(i)
                features.extend(f)
                labels.extend(l)

        print("Loaded %d rows" % len(features))

        return ids, features, labels

    def batch(self, uids, size):
        """
        Splits uids into batches.

        Args:
            uids: uids
            size: batch size

        Returns:
            list of lists split into batch size
        """

        return [uids[x:x + size] for x in range(0, len(uids), size)]

    def transform(self, rows, uids):
        """
        Transforms a list of rows into features and labels.

        Args:
            rows: input rows
            uids: uid to label mapping

        Returns:
            (features, labels)
        """

        ids = []
        features = []
        labels = []

        # Retrieve all rows and group by article id
        for uid, sections in groupby(rows, lambda x: x[2]):
            # Get sections as list
            sections = list(sections)

            # Save ids, features and label
            ids.append(uid)
            features.append(self.features(sections))
            labels.append(uids[uid])

        return ids, features, labels

    def features(self, sections):
        """
        Builds a features vector from input text.

        Args:
            sections: list of sections

        Returns:
            features vector as a list
        """

        # Feature vector
        vector = []

        # Build title keyword features
        title = [text for name, text, _ in sections if name == "TITLE"]
        title = title[0].lower() if title else None

        for keyword in Vocab.TITLE:
            vector.append(len(re.findall("\\b%s\\b" % keyword.lower(), title)) if title else 0)

        # Build full text from filtered sections
        text = [text for name, text, _ in sections if not name or StudyModel.filter(name.lower())]
        text = " ".join(text).replace("\n", " ").lower()

        # Get token length across filtered sections
        length = sum([len(tokens) for name, _, tokens in sections if not name or StudyModel.filter(name.lower())])

        # Add study design term counts normalized by document length
        for keyword in self.keywords:
            vector.append(len(re.findall("\\b%s\\b" % keyword.lower(), text)) / length)

        return vector

    @staticmethod
    def run(training, path, optimize):
        """
        Trains a new model.

        Args:
            training: path to training file
            path: database path
            optimize: if hyperparameter optimization should be enabled
        """

        # Load articles database
        db = sqlite3.connect(path)

        try:
            # Train the model
            model = Design()
            model.train((training, db), optimize)

            # Save the model
            print("Saving model to %s" % path)
            model.save(os.path.join(path, "design"))

        finally:
            db.close()

if __name__ == "__main__":
    Design.run(sys.argv[1] if len(sys.argv) > 1 else None,
               sys.argv[2] if len(sys.argv) > 2 else None,
               sys.argv[3] == "1" if len(sys.argv) > 3 else False)
