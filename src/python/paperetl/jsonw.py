"""
JSON writer module
"""

import json
import os

import numpy as np

from .database import Database

class JSON(Database):
    """
    Defines data structures and methods to store articles as JSON files.
    """

    def __init__(self, outdir):
        """
        Creates and initializes an output directory to use for writing JSON files.

        Args:
            outdir: output directory
        """

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        self.outdir = outdir

    def save(self, article):
        output = os.path.splitext(article.source if article.source else article.uid())[0] + ".json"

        with open(os.path.join(self.outdir, output), "w") as output:
            json.dump(article.build(), output, cls=NumPyEncoder)

class NumPyEncoder(json.JSONEncoder):
    """
    Custom encoder to handle numpy values
    """

    # pylint: disable=E0202, W0221
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumPyEncoder, self).default(obj)
