"""
Analysis module
"""

import os

import numpy as np

from .study.attribute import Attribute
from .study.design import Design
from .study.sample import Sample

# Global helper for multi-processing support
# pylint: disable=W0603
MODELS = None

def getModels(models):
    """
    Multiprocessing helper method. Gets (or first creates then gets) a global study models object to
    be accessed in a new subprocess.

    Args:
        models: models directory

    Returns:
        (attribute model, design model)
    """

    global MODELS

    if not MODELS:
        attribute = Attribute()
        attribute.load(os.path.join(models, "attribute"))

        design = Design()
        design.load(os.path.join(models, "design"))

        MODELS = (attribute, design)

    return MODELS

class Study(object):
    """
    Study design parser. Derives study design fields using a series of machine learning models and NLP analysis.
    """

    @staticmethod
    def parse(sections, models):
        """
        Parses study design fields contained within an article.

        Args:
            sections: list of text sections
            models: models directory

        Returns:
            study design fields as tuple
        """

        # Return default values if sections is empty
        if not sections:
            return (0, None, None, None, [])

        # Get design models
        attribute, design = getModels(models)

        # Study design type
        design = design.predict(sections)

        # Detect attributes within sections
        attributes = attribute.predict(sections)

        # Extract sample size, sample, method
        size, sample, method = Sample.extract(sections, attributes)

        # Label each section
        labels = []
        for x, (_, text, _) in enumerate(sections):
            # Get predicted attribute
            attribute = np.argmax(attributes[x])
            label = None

            if attribute == 1:
                label = "STATISTIC"
            elif text == sample:
                label = "SAMPLE_SIZE"
            elif text == method:
                label = "SAMPLE_METHOD"

            labels.append(label)

        return (design, size, sample, method, labels)
