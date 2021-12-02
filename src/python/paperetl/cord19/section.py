"""
Section module
"""

import json
import os
import re

from nltk.tokenize import sent_tokenize

from ..table import Table
from ..text import Text


class Section:
    """
    Parses text content from JSON file sections.
    """

    @staticmethod
    def parse(row, directory):
        """
        Reads title, abstract and body text for a given row. Text is returned as a list of sections.

        Args:
            row: input row
            directory: input directory

        Returns:
            list of text sections
        """

        sections = []

        # Add title and abstract sections
        for name in ["title", "abstract"]:
            text = row[name]
            if text:
                # Remove leading and trailing []
                text = re.sub(r"^\[", "", text)
                text = re.sub(r"\]$", "", text)

                # Transform and clean text
                text = Text.transform(text)

                sections.extend([(name.upper(), x) for x in sent_tokenize(text)])

        # Process each JSON file
        for path in Section.files(row):
            # Build article path
            article = os.path.join(directory, path)

            try:
                with open(article, encoding="utf-8") as jfile:
                    data = json.load(jfile)

                    # Extract text from body
                    for section in data["body_text"]:
                        # Section name and text
                        name = (
                            section["section"].upper()
                            if len(section["section"].strip()) > 0
                            else None
                        )
                        text = section["text"].replace("\n", " ")

                        # Clean and transform text
                        text = Text.transform(text)

                        # Split text into sentences, transform text and add to sections
                        sections.extend([(name, x) for x in sent_tokenize(text)])

                    # Extract text from tables
                    for name, entry in data["ref_entries"].items():
                        if "html" in entry and entry["html"]:
                            sections.extend(
                                [(name, x) for x in Table.parse(entry["html"])]
                            )

            # pylint: disable=W0703
            except Exception as ex:
                print(f"Error processing text file: {article}", ex)

        # Filter out boilerplate elements from text
        return Section.filtered(sections)

    @staticmethod
    def files(row):
        """
        Build a list of json file paths to parse.

        Args:
            row: input row

        Returns:
            list of paths
        """

        paths = []

        # Build list of documents to parse
        for column in ["pdf_json_files", "pmc_json_files"]:
            if row[column]:
                paths.extend(row[column].split("; "))

        return paths

    @staticmethod
    def filtered(sections):
        """
        Returns a filtered list of text sections. Duplicate and boilerplate text strings are removed.

        Args:
            sections: input sections

        Returns:
            filtered list of sections
        """

        # Use list to preserve insertion order
        unique = []
        keys = set()

        # Boilerplate text to ignore
        boilerplate = [
            "COVID-19 resource centre",
            "permission to make all its COVID",
            "WHO COVID database",
            "COVID-19 public health emergency response",
        ]

        for name, text in sections:
            # Add unique text that isn't boilerplate text
            if not text in keys and not any(x in text for x in boilerplate):
                unique.append((name, text))
                keys.add(text)

        return unique
