"""
Study module
"""

import math
import pickle

import numpy as np
import regex as re

from sklearn.metrics import accuracy_score, log_loss, f1_score
from sklearn.model_selection import train_test_split, GridSearchCV

from .vocab import Vocab

class StudyModel(object):
    """
    Base StudyModel class used for study classifiers.
    """

    SECTION_FILTER = r"background|(?<!.*?results.*?)discussion|introduction|reference"

    @staticmethod
    def getKeywords(design=True, sample=True, method=True):
        """
        Generates an unique keyword vector list.

        Returns:
            list of keyword regular expressions
        """

        keywords = []
        if design:
            keywords = keywords + Vocab.DESIGN
        if sample:
            keywords = keywords + Vocab.SAMPLE
        if method:
            keywords = keywords + Vocab.METHOD

        # Deduplicate keywords
        return sorted(set(keywords))

    @staticmethod
    def filter(name):
        """
        Filters a section name. Returns True if name is a title, method or results section.

        Args:
            name: section name

        Returns:
            True if section should be analyzed, False otherwise
        """

        # Skip background, introduction and reference sections
        # Skip discussion unless it's a results and discussion
        return not re.search(StudyModel.SECTION_FILTER, name)

    def __init__(self):
        """
        Builds a new StudyModel.
        """

        # Prediction model
        self.model = None
        self.tfidf = None

        # Keywords
        self.keywords = None

    def load(self, path):
        """
        Loads a StudyModel.

        Args:
            path: path to model
        """

        with open(path, "rb") as handle:
            self.__dict__ = pickle.load(handle)

    def save(self, path):
        """
        Saves a StudyModel.

        Args:
            path: path to model
        """

        with open(path, "wb") as handle:
            pickle.dump(self.__dict__, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def train(self, training, optimize, validate):
        """
        Trains a new model.

        Args:
            training: training data
            optimize: optional hyperparameter optimization settings, if None optimization is skipped
            validate: if training data should be validated through model after training
        """

        # Create model, parameters set via hyperparameter tuning
        model = self.create()

        # Enable hyperparameter optimization for this run
        if optimize:
            params = self.hyperparams()
            model = GridSearchCV(model, params, cv=optimize.get("cv", 5), verbose=optimize.get("verbose", 1),
                                 n_jobs=optimize.get("n_jobs", -1))

        # Load training data
        ids, features, labels = self.data(training)

        # Split into train/test
        x_train, x_test, y_train, y_test = train_test_split(features, labels, test_size=0.1, random_state=0)

        # Fit the model
        model.fit(x_train, y_train)

        # Reporting
        if optimize:
            print("Optimal Parameters - ", model.best_params_)

        # Store model
        self.model = model

        # Score model
        self.score(x_test, y_test)

        # Test model predictions on ALL training data
        # Helps show records model is confused about within training data
        if validate:
            for i, x in enumerate(features):
                pred = model.predict([x])
                if not np.array_equal(pred[0], labels[i]):
                    print(ids[i], labels[i], ", WRONG: ", pred)

    def score(self, features, labels):
        """
        Scores the model accuracy for test data.

        Args:
            features: test features
            labels: test labels
        """

        predictions = self.model.predict_proba(features)
        size = range(len(predictions[0]))
        multiclass = False

        # Handle both single-class and multi-class labels
        if isinstance(labels, np.ndarray):
            plabels = [[x >= 0.5 for x in p] for p in predictions]
            multiclass = True
        else:
            plabels = [p.argmax() for p in predictions]

        print("Test Accuracy: ", accuracy_score(labels, plabels))
        print("Test F1 Score: ", f1_score(labels, plabels, labels=size, average="weighted", zero_division=0))
        print("Test Log Loss: ", log_loss(labels, predictions, labels=size if not multiclass else None))
        print("Base Log Loss (nclass=%d): " % len(size), -math.log(1 / len(size)))

    def predict(self, sections):
        """
        Classifies sections using a prediction model.

        Args:
            sections: list of text sections

        Returns:
            (label, probability array)
        """

    def create(self):
        """
        Creates a new model.

        Returns:
            (model, tfidf)
        """

        return (None, None)

    def hyperparams(self):
        """
        Returns a range of hyperparameters.

        Returns:
            dict of hyperparameter ranges
        """

        return {}

    def data(self, training):
        """
        Reads training data.

        Args:
            training: training input file

        Returns:
            (ids, features, labels)
        """

        return (training, training, training)
