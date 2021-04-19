"""
Transforms and loads medical/scientific files into an articles database.
"""

import os

from ..factory import Factory

from .csvf import CSV
from .pdf import PDF
from .tei import TEI

class Execute(object):
    """
    Transforms and loads medical/scientific files into an articles database.
    """

    @staticmethod
    def process(stream, source, models, extension):
        """
        Processes a data input stream and yields articles

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
            models: path to study models
            format: data format
        """

        if extension == "pdf":
            yield PDF.parse(stream, source, models)
        elif extension == "xml":
            yield TEI.parse(stream, source, models)
        elif extension == "csv":
            yield from CSV.parse(stream, source, models)

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

        # Processed ids
        ids = set()

        # Recursively walk directory looking for files
        for root, _, files in sorted(os.walk(indir)):
            for f in sorted(files):
                # Extract file extension
                extension = f.split(".")[-1].lower()

                # Check if file ends with accepted extension
                if any([extension for ext in ["csv", "pdf", "xml"]]):
                    # Build full path to file
                    path = os.path.join(root, f)

                    # Determine if file needs to be open in binary or text mode
                    mode = "rb" if extension == "pdf" else "r"

                    print("Processing: %s" % path)
                    with open(path, mode) as data:
                        # Yield articles from input stream
                        for article in Execute.process(data, f, models, extension):
                            # Save article if unique
                            if article and article.uid() not in ids:
                                db.save(article)
                                ids.add(article.uid())

        # Complete and close database
        db.complete()
        db.close()
