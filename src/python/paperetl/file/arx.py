"""
arXiv XML processing module
"""

import hashlib
import re

from bs4 import BeautifulSoup
from dateutil import parser
from nltk.tokenize import sent_tokenize

from ..schema.article import Article
from ..text import Text


class ARX:
    """
    Methods to transform arXiv XML into article objects.
    """

    @staticmethod
    def parse(stream, source):
        """
        Parses a XML datastream and yields processed articles.

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
            config: path to config directory
        """

        # Parse XML
        soup = BeautifulSoup(stream, "lxml")

        # Process each entry
        for entry in soup.find_all("entry"):
            reference = ARX.get(entry, "id")
            title = ARX.get(entry, "title")
            published = parser.parse(ARX.get(entry, "published").split("T")[0])
            updated = parser.parse(ARX.get(entry, "updated").split("T")[0])

            # Derive uid
            uid = hashlib.sha1(reference.encode("utf-8")).hexdigest()

            # Get journal reference
            journal = ARX.get(entry, "arxiv:journal_ref")

            # Get authors
            authors, affiliations, affiliation = ARX.authors(entry.find_all("author"))

            # Get tags
            tags = "; ".join(
                ["ARX"]
                + [category.get("term") for category in entry.find_all("category")]
            )

            # Transform section text
            sections = ARX.sections(title, ARX.get(entry, "summary"))

            # Article metadata - id, source, published, publication, authors, affiliations, affiliation, title,
            #                    tags, reference, entry date
            metadata = (
                uid,
                source,
                published,
                journal,
                authors,
                affiliations,
                affiliation,
                title,
                tags,
                reference,
                updated,
            )

            yield Article(metadata, sections)

    @staticmethod
    def get(element, path):
        """
        Finds the first matching path in element and returns the element text.

        Args:
            element: XML element
            path: path expression

        Returns:
            string
        """

        element = element.find(path)
        return ARX.clean(element.text) if element else None

    @staticmethod
    def clean(text):
        """
        Removes newlines and extra spacing from text.

        Args:
            text: text to clean

        Returns:
            clean text
        """

        # Remove newlines and cleanup spacing
        text = text.replace("\n", " ")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def authors(elements):
        """
        Parses authors and associated affiliations from the article.

        Args:
            elements: authors elements

        Returns:
            (semicolon separated list of authors, semicolon separated list of affiliations, primary affiliation)
        """

        authors = []
        affiliations = []

        for author in elements:
            # Create authors as lastname, firstname
            name = ARX.get(author, "name")
            authors.append(", ".join(name.rsplit(maxsplit=1)[::-1]))

            # Add affiliations
            affiliations.extend(
                [
                    ARX.clean(affiliation.text)
                    for affiliation in author.find_all("arxiv:affiliation")
                ]
            )

        return (
            "; ".join(authors),
            "; ".join(dict.fromkeys(affiliations)),
            affiliations[-1] if affiliations else None,
        )

    @staticmethod
    def sections(title, text):
        """
        Gets a list of sections for this article.

        Args:
            title: title string
            text: summary text

        Returns:
            list of sections
        """

        # Add title
        sections = [("TITLE", title)]

        # Transform and clean text
        text = Text.transform(text)

        # Split text into sentences, transform text and add to sections
        sections.extend([("ABSTRACT", x) for x in sent_tokenize(text)])

        return sections
