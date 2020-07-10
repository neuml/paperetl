"""
Section module
"""

import json
import os
import re

from nltk.tokenize import sent_tokenize

from ..table import Table

# Compiled pattern for cleaning text
# pylint: disable=W0603
PATTERN = None

def getPattern():
    """
    Gets or builds a pre-compiled regex for cleaning text.

    Returns:
        compiled regex
    """

    global PATTERN

    if not PATTERN:
        # List of patterns
        patterns = []

        # Remove emails
        patterns.append(r"\w+@\w+(\.[a-z]{2,})+")

        # Remove urls
        patterns.append(r"http(s)?\:\/\/\S+")

        # Remove single characters repeated at least 3 times (ex. j o u r n a l)
        patterns.append(r"(^|\s)(\w\s+){3,}")

        # Remove citations references (ex. [3] [4] [5])
        patterns.append(r"(\[\d+\]\,?\s?){3,}(\.|\,)?")

        # Remove citations references (ex. [3, 4, 5])
        patterns.append(r"\[[\d\,\s]+\]")

        # Remove citations references (ex. (NUM1) repeated at least 3 times with whitespace
        patterns.append(r"(\(\d+\)\s){3,}")

        PATTERN = re.compile("|".join(["(%s)" % p for p in patterns]))

    return PATTERN

class Section(object):
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
        citations = []

        # Add title and abstract sections
        for name in ["title", "abstract"]:
            text = row[name]
            if text:
                # Remove leading and trailing []
                text = re.sub(r"^\[", "", text)
                text = re.sub(r"\]$", "", text)

                # Transform and clean text
                text = Section.transform(text)

                sections.extend([(name.upper(), x) for x in sent_tokenize(text)])

        # Process each JSON file
        for path in Section.files(row):
            # Build article path
            article = os.path.join(directory, path)

            try:
                with open(article) as jfile:
                    data = json.load(jfile)

                    # Extract text from body
                    for section in data["body_text"]:
                        # Section name and text
                        name = section["section"].upper() if len(section["section"].strip()) > 0 else None
                        text = section["text"].replace("\n", " ")

                        # Clean and transform text
                        text = Section.transform(text)

                        # Split text into sentences, transform text and add to sections
                        sections.extend([(name, x) for x in sent_tokenize(text)])

                    # Extract text from tables
                    for name, entry in data["ref_entries"].items():
                        if "html" in entry and entry["html"]:
                            sections.extend([(name, x) for x in Table.parse(entry["html"])])

                    # Extract citations
                    citations.extend([entry["title"] for entry in data["bib_entries"].values()])

            # pylint: disable=W0703
            except Exception as ex:
                print("Error processing text file: {}".format(article), ex)

        # Filter out boilerplate elements from text
        return Section.filtered(sections, citations)

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
    def transform(text):
        """
        Transforms and cleans text to help improve text indexing accuracy.

        Args:
            text: input text line

        Returns:
            transformed text
        """

        # Clean/transform text
        text = getPattern().sub(" ", text)

        # Remove extra spacing either caused by replacements or already in text
        text = re.sub(r" {2,}|\.{2,}", " ", text)

        return text

    @staticmethod
    def filtered(sections, citations):
        """
        Returns a filtered list of text sections and citations. Duplicate and boilerplate text strings are removed.

        Args:
            sections: input sections
            citations: input citations

        Returns:
            filtered list of sections, citations
        """

        # Use list to preserve insertion order
        unique = []
        keys = set()

        # Boilerplate text to ignore
        boilerplate = ["COVID-19 resource centre", "permission to make all its COVID", "WHO COVID database",
                       "COVID-19 public health emergency response"]

        for name, text in sections:
            # Add unique text that isn't boilerplate text
            if not text in keys and not any([x in text for x in boilerplate]):
                unique.append((name, text))
                keys.add(text)

        return unique, list(set(citations))
