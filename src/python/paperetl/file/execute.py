"""
Transforms and loads medical/scientific files into an articles database.
"""

import os

from ..factory import Factory

from .csvf import CSV
from .pdf import PDF
from .pmb import PMB
from .tei import TEI


class Execute:
    """
    Transforms and loads medical/scientific files into an articles database.
    """

    @staticmethod
    def mode(source, extension):
        """
        Determines file open mode for source file.

        Args:
            source: text string describing stream source, can be None
            extension: data format

        Returns:
            file open mode
        """

        return (
            "rb"
            if extension == "pdf" or (source and source.lower().startswith("pubmed"))
            else "r"
        )

    @staticmethod
    def process(stream, source, extension, config):
        """
        Processes a data input stream and yields articles

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
            extension: data format
            config: path to config directory
        """

        if extension == "pdf":
            yield PDF.parse(stream, source)
        elif extension == "xml":
            if source and source.lower().startswith("pubmed"):
                yield from PMB.parse(stream, source, config)
            else:
                yield TEI.parse(stream, source)
        elif extension == "csv":
            yield from CSV.parse(stream, source)

    @staticmethod
    def run(indir, url, config=None):
        """
        Main execution method.

        Args:
            indir: input directory
            url: database url
            config: path to config directory, if any
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
                if any(extension for ext in ["csv", "pdf", "xml"]):
                    # Build full path to file
                    path = os.path.join(root, f)

                    # Determine if file needs to be open in binary or text mode
                    mode = Execute.mode(f, extension)

                    print(f"Processing: {path}")
                    with open(path, mode) as data:
                        # Yield articles from input stream
                        for article in Execute.process(data, f, extension, config):
                            # Save article if unique
                            if article and article.uid() not in ids:
                                db.save(article)
                                ids.add(article.uid())

        # Complete and close database
        db.complete()
        db.close()
