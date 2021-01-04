"""
Attribute module
"""

import csv
import os
import sys

import numpy as np
import regex as re
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from .sample import Sample
from .study import StudyModel
from .vocab import Vocab

class Attribute(StudyModel):
    """
    Prediction model used to classify study attributes such as the sample size, sampling method or risk factors.
    """

    def __init__(self):
        """
        Builds a new Attribute detection model.

        Args:
            training: path to training data
            models: path to models
        """

        super(Attribute, self).__init__()

        # Keywords to use as features
        self.keywords = StudyModel.getKeywords(design=False)

        # TF-IDF vectors
        self.tfidf = None

    def predict(self, sections):
        # Build features array for document
        text = [text for name, text, _ in sections if not name or StudyModel.filter(name.lower())]

        features = [self.features(text, tokens) for name, text, tokens in sections]

        # Build tf-idf vector
        vector = self.tfidf.transform([text for text, _ in features])

        # Concat tf-idf and features vector
        features = np.concatenate((vector.toarray(), [f for _, f in features]), axis=1)

        # Predict probability - run serially for each row to prevent multi-threaded GIL thrashing
        predictions = np.array([self.model.predict_proba([f])[0] for f in features])

        # Clear predictions for short text snippets and filtered sections
        for x, (name, text, _) in enumerate(sections):
            if len(text) <= 25 or (name and not StudyModel.filter(name.lower())):
                # Clear prediction
                # pylint: disable=E1136
                predictions[x] = np.zeros(predictions.shape[1])

        return predictions

    def create(self):
        return OneVsRestClassifier(LogisticRegression(C=0.995, solver="lbfgs", max_iter=1000, random_state=0))

    def hyperparams(self):
        return {"estimator__C": [x / 200 for x in range(100, 300)],
                "estimator__solver": ("lbfgs", "liblinear"),
                "estimator__max_iter": (1000,),
                "estimator__random_state": (0,)}

    def data(self, training):
        # Features
        ids = []
        features = []
        labels = []

        # Load NLP model to parse tokens
        nlp = spacy.load("en_core_sci_md")

        # Read training data, convert to features
        with open(training, mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                # Parse text tokens
                text = row["text"]
                tokens = nlp(text)

                # Store ids, features and labels
                ids.append(text)
                features.append(self.features(text, tokens))
                labels.append([int(label) for label in row["label"].split(":")])

        # Build tf-idf model across dataset, concat with feature vector
        self.tfidf = TfidfVectorizer()
        vector = self.tfidf.fit_transform([text for text, _ in features])
        features = np.concatenate((vector.toarray(), [f for _, f in features]), axis=1)

        print("Loaded %d rows" % len(features))

        labels = MultiLabelBinarizer().fit_transform(labels)

        return ids, features, labels

    def features(self, text, tokens):
        """
        Builds a features vector from input text.

        Args:
            sections: list of sections

        Returns:
            features vector as a list
        """

        # Feature vector
        vector = []

        # Add study design term counts normalized by number of tokens
        for keyword in self.keywords:
            vector.append(len(re.findall("\\b%s\\b" % keyword.lower(), text.lower())) / len(tokens))

        pos = [token.pos_ for token in tokens]
        dep = [token.dep_ for token in tokens]

        # Append entity count (scispacy only tracks generic entities) normalized by number of tokens
        vector.append(len([entity for entity in tokens.ents if entity.text.lower() in self.keywords]) / len(tokens))

        # Append part of speech counts normalized by number of tokens
        for name in ["ADJ", "ADP", "ADV", "AUX", "CONJ", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PUNCT",
                     "SCONJ", "SYM", "VERB", "X", "SPACE"]:
            vector.append(pos.count(name) / len(tokens))

        # Append dependency counts normalized by number of tokens
        for name in ["acl", "advcl", "advmod", "amod", "appos", "aux", "case", "cc", "ccomp", "clf", "compound",
                     "conj", "cop", "csubj", "dep", "det", "discourse", "dislocated", "expl", "fixed", "flat",
                     "goeswith", "iobj", "list", "mark", "nmod", "nsubj", "nummod", "obj", "obl", "orphan",
                     "parataxis", "punct", "reparandum", "root", "vocative", "xcomp"]:
            vector.append(dep.count(name) / len(tokens))

        # Descriptive numbers on sample identifiers - i.e. 34 patients, 15 subjects, ten samples
        vector.append(1 if Sample.find(tokens, Vocab.SAMPLE) else 0)

        # Regular expression for dates
        dateregex = r"(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|" + \
                    r"September|Sep|October|Oct|November|Nov|December|Dec)\s?\d{1,2}?,? \d{4}?"

        # Dates within the string normalized by number of tokens
        dates = len(re.findall(dateregex, text))
        vector.append(dates / len(tokens))

        return (text, vector)

    @staticmethod
    def run(training, path, optimize, validate):
        """
        Trains a new model.

        Args:
            training: path to training file
            path: models path
            optimize: optional hyperparameter grid search settings, if None optimization is skipped
            validate: if training data should be validated through model after training
        """

        # Train the model
        model = Attribute()
        model.train(training, optimize, validate)

        # Save the model
        print("Saving model to %s" % path)
        model.save(os.path.join(path, "attribute"))

if __name__ == "__main__":
    Attribute.run(sys.argv[1] if len(sys.argv) > 1 else None,
                  sys.argv[2] if len(sys.argv) > 2 else None,
                  {"cv": int(sys.argv[3])} if len(sys.argv) > 3 else None,
                  sys.argv[4] if len(sys.argv) > 4 else False)
