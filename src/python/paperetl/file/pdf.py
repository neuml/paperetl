"""
PDF processing module
"""

from io import StringIO

import requests

from .tei import TEI

class PDF(object):
    """
    Methods to transform medical/scientific PDFs into article objects.
    """

    @staticmethod
    def parse(stream, source, models):
        """
        Parses a medical/scientific PDF datastream and returns a processed article.

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
            models: path to study models

        Returns:
            (uid, article metadata, section text, article tags, study design)
        """

        # Convert PDF stream to TEI XML, parse and return object
        return TEI.parse(PDF.convert(stream), source, models)

    @staticmethod
    def convert(stream):
        """
        Converts a medical/scientific article PDF into TEI XML via a GROBID Web Service API call.

        Args:
            stream: handle to input data stream

        Returns:
            TEI XML stream
        """

        # Call GROBID API
        data = requests.post("http://localhost:8070/api/processFulltextDocument", files={"input": stream}).text

        # Wrap as StringIO
        return StringIO(data)
