"""
Transforms and loads medical/scientific files into an articles database.
"""

import os

from ..factory import Factory
from .pdf import PDF
from .tei import TEI

class Execute(object):
    """
    Transforms and loads medical/scientific files into an articles database.
    """

    @staticmethod
    def run(indir, url, models):
        """
        Main execution method.

        Args:
            indir: input directory
            url: database url
            models: model directory
        """

        # Build database connection
        db = Factory.create(url)

        # Recursively walk directory looking for files
        for root, _, files in sorted(os.walk(indir)):
            for f in sorted(files):
                # Check if file ends with accepted extension
                if any([f.lower().endswith(ext) for ext in ["pdf", "xml"]]):
                    isPdf = f.lower().endswith("pdf")

                    # Build full path to file
                    path = os.path.join(root, f)

                    print("Processing: %s" % path)
                    with open(path, "rb" if isPdf else "r") as data:
                        # Parse and save record
                        db.save(PDF.parse(data, f, models) if isPdf else TEI.parse(data, f, models))

        # Complete and close database
        db.complete(None)
        db.close()
