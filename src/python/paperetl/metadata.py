"""
Metadata module. Derives additional metadata fields.
"""

import os

import numpy as np

from .study.attribute import Attribute
from .study.design import Design
from .study.sample import Sample

# Global helper for multi-processing support
# pylint: disable=W0603
MODELS = None

def getModels(outdir):
    """
    Multiprocessing helper method. Gets (or first creates then gets) a global study models object to
    be accessed in a new subprocess.

    Returns:
        (attribute model, design model)
    """

    global MODELS

    if not MODELS:
        attribute = Attribute()
        attribute.load(os.path.join(outdir, "attribute"))

        design = Design()
        design.load(os.path.join(outdir, "design"))

        MODELS = (attribute, design)

    return MODELS

class Metadata(object):
    """
    Methods to derive additional metadata fields for a study contained within an article.
    """

    @staticmethod
    def parse(sections, outdir):
        """
        Parses metadata fields contained within an article.

        Args:
            sections: list of text sections
            outdir: output directory

        Returns:
            metadata fields as tuple
        """

        # Get design models
        attribute, design = getModels(outdir)

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
