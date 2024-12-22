"""
CSV processing module
"""

import csv
import datetime

from dateutil import parser

from ..schema.article import Article


class CSV:
    """
    Methods to transform CSVs into article objects.
    """

    @staticmethod
    def parse(stream, source):
        """
        Parses a CSV datastream and yields processed articles.

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
        """

        for row in csv.DictReader(stream):
            # Parse metadata
            metadata = CSV.metadata(row, source)

            # Parse sections
            sections = CSV.sections(row)

            yield Article(metadata, sections)

    @staticmethod
    def metadata(row, source):
        """
        Parses a metadata tuple from input CSV row.

        Args:
            row: dict record with fields
            source: text string describing stream source, can be None

        Returns:
            metadata tuple
        """

        # Article metadata - id, source, published, publication, authors, affiliations, affiliation, title,
        #                    tags, reference, entry date
        fields = (
            "id",
            "source",
            "published",
            "publication",
            "authors",
            "affiliations",
            "affiliation",
            "title",
            "tags",
            "reference",
            "entry",
        )

        metadata = []
        for field in fields:
            value = None
            if field == "source":
                value = row.get(field, source)
            elif field == "entry":
                # Parse date field if found, otherwise use current date
                value = row.get(field)
                value = parser.parse(value if value else datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                value = row.get(field)

            metadata.append(value)

        return tuple(metadata)

    @staticmethod
    def sections(row):
        """
        Parses section text data from input CSV row.

        Args:
            row: dict record with fields

        Returns:
            list of sections
        """

        # Start with title as text
        text = row.get("title")

        # Append abstract if available
        abstract = row.get("abstract")
        if abstract:
            text += " " + abstract

        # Create single section from text
        return [(None, text)]
