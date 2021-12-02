"""
Transforms and loads PubMed archive XML files into an articles database.
"""

import datetime
import os
import re

from dateutil import parser
from lxml import etree
from nltk.tokenize import sent_tokenize

from ..schema.article import Article
from ..text import Text


class PMB:
    """
    Methods to transform PubMed archive XML files into article objects.
    """

    # pylint: disable=W0613
    @staticmethod
    def parse(stream, source, config):
        """
        Parses a XML datastream and yields processed articles.

        Args:
            stream: handle to input data stream
            source: text string describing stream source, can be None
            config: path to config directory
        """

        # Load MeSH filter codes if available
        codes = None
        path = os.path.join(config, "codes") if config else None
        if path and os.path.exists(path):
            with open(os.path.join(config, "codes"), encoding="utf-8") as f:
                codes = set(line.strip() for line in f)

        # Parse HTML content using lxml
        # pylint: disable=c-extension-no-member,stop-iteration-return
        document = etree.iterparse(stream, events=("start", "end"))
        _, root = next(document)

        for event, element in document:
            if event == "end" and element.tag == "PubmedArticle":
                yield PMB.process(element, source, codes)
                root.clear()

    @staticmethod
    def process(element, source, codes):
        """
        Processes a single XML article element into an Article.

        Args:
            element: XML element
            source: text string describing stream source, can be None
            codes: List of MeSH codes to filter, can be None

        Returns:
            Article or None if Article not parsed
        """

        citation = element.find("MedlineCitation")
        article = citation.find("Article")
        journal = article.find("Journal")

        # General fields
        uid = int(citation.find("PMID").text)
        source = source if source else "PMB"
        reference = f"https://pubmed.ncbi.nlm.nih.gov/{uid}"

        # Journal fields
        published = PMB.date(journal)
        publication = PMB.get(journal, "Title")

        # Article fields
        title = PMB.get(article, "ArticleTitle")
        authors, affiliations, affiliation = PMB.authors(article)

        # MeSH codes for filtering, always match if no target MeSH codes available
        mesh = PMB.mesh(citation)
        match = [x for x in mesh if x in codes] if codes else True

        # Create tags
        tags = "; ".join(["PMB"] + mesh)

        # Abstract text
        sections = PMB.sections(article, title)

        if len(sections) > 1 and (match or not mesh):
            # Article metadata - id, source, published, publication, authors, affiliations, affiliation, title,
            #                    tags, reference, entry date
            metadata = (
                str(uid),
                source,
                published,
                publication,
                authors,
                affiliations,
                affiliation,
                title,
                tags,
                reference,
                datetime.datetime.now().strftime("%Y-%m-%d"),
            )

            return Article(metadata, sections, source)

        return None

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
        return PMB.text(element)

    @staticmethod
    def text(element):
        """
        Flattens elements into a single text string.

        Args:
            element: XML element

        Returns:
            string
        """

        return "".join(element.itertext()) if element is not None else None

    @staticmethod
    def date(journal):
        """
        Parses the published date. Multiple date formats are handled via the
        dateparser library.

        Args:
            journal: journal element

        Returns:
            datetime
        """

        element = journal.find("JournalIssue/PubDate")

        date = ""
        for field in ["Year", "Month", "Day"]:
            value = PMB.get(element, field)
            if value:
                date += "-" + value if date else value

        if not date:
            # Attempt to parse out date
            date = PMB.get(element, "MedlineDate")
            date = re.search(r"\d{4}", date)
            date = date.group() if date else None

        return parser.parse(date) if date else None

    @staticmethod
    def authors(journal):
        """
        Parses authors and associated affiliations from the article.

        Args:
            journal: journal element

        Returns:
            (semicolon separated list of authors, semicolon separated list of affiliations, primary affiliation)
        """

        authors = []
        affiliations = []

        for author in journal.findall("AuthorList/Author"):
            lastname = PMB.get(author, "LastName")
            forename = PMB.get(author, "ForeName")

            # Add author affiliations
            for affiliation in author.findall("AffiliationInfo/Affiliation"):
                affiliations.append(PMB.text(affiliation))

            if lastname and forename:
                authors.append(f"{lastname}, {forename}")

        return (
            "; ".join(authors),
            "; ".join(dict.fromkeys(affiliations)),
            affiliations[-1] if affiliations else None,
        )

    @staticmethod
    def mesh(citation):
        """
        Gets a list of article MeSH codes.

        Args:
            citation: citation element

        Returns:
            list of MeSH codes
        """

        return [
            descriptor.attrib["UI"]
            for descriptor in citation.findall("MeshHeadingList//DescriptorName")
            if descriptor.attrib["UI"]
        ]

    @staticmethod
    def sections(article, title):
        """
        Gets a list of sections for this article. This method supports the following three abstract formats:
           - Raw text
           - HTML formatted text
           - Abstract text parsed into section named elements

        All three formats return sections that are tokenized into sentences.

        Args:
            article: article element
            title: title string

        Returns:
            list of sections
        """

        sections = [("TITLE", title)] if title else []

        # Get AbstractText elements
        elements = article.findall("Abstract/AbstractText")

        if len(elements) == 1:
            element = elements[0]
            if element.text:
                # Process abstract as raw text
                sections.extend(PMB.raw(element))
            else:
                # Process abstract as formatted text
                sections.extend(PMB.formatted(element))
        else:
            # Process abstract as parsed elements with section names
            sections.extend(PMB.parsed(elements))

        return sections

    @staticmethod
    def raw(element):
        """
        Parses a raw text abstract into a list of sections.

        Args:
            element: abstract text element

        Returns:
            list of sections
        """

        # Transform and clean text
        text = Text.transform(PMB.text(element))

        # No embedded sections
        return [("ABSTRACT", x) for x in sent_tokenize(text)]

    @staticmethod
    def formatted(element):
        """
        Parses a HTML formatted text abstract into a list of sections.

        Args:
            element: abstract text element

        Returns:
            list of sections
        """

        sections = []
        name, tag, texts = "ABSTRACT", None, []

        for x in element.getchildren():
            # Get raw tag text and clean tag text
            rtext = "".join(x.itertext())
            ctext = PMB.section(rtext)
            new = False

            # Set section tag type if all of the following:
            #   - tag not set
            #   - cleaned inner text has data
            #   - no section text queued
            #   - element tag is a <b> or matches a defined section background category name
            if (
                not tag
                and ctext
                and not texts
                and (x.tag.lower() == "b" or PMB.background(ctext))
            ):
                tag = x.tag

            # New section if one of following:
            #   - element tag matches section tag and tag text has data
            #   - no section tag and section text is queued
            # AND
            #   - no section text
            #   - last section text element ends in period
            # pylint: disable=R0916
            if ((x.tag == tag and ctext) or (not tag and texts)) and (
                not texts or texts[-1].strip().endswith(".")
            ):
                # Save previous section
                if texts:
                    sections.extend(
                        [(name, t) for t in sent_tokenize("".join(texts).strip())]
                    )

                # Reset section name/texts
                name = ctext if tag else "ABSTRACT"
                texts = []
                new = True

            # Create section text. Skip tag text for section names.
            text = rtext if not new and ctext else ""
            text += x.tail if x.tail else ""
            if text.strip():
                texts.append(text)

        # Save last section
        if texts:
            sections.extend([(name, t) for t in sent_tokenize("".join(texts).strip())])

        return sections

    @staticmethod
    def parsed(elements):
        """
        Parses a labeled text abstract into a list of sections.

        Args:
            element: abstract text element

        Returns:
            list of sections
        """

        sections = []

        # Parsed abstract
        for element in elements:
            name = (
                PMB.section(element.attrib["Label"])
                if "Label" in element.attrib
                else None
            )
            name = name if name else "ABSTRACT"

            if element.text:
                # Transform and clean text
                text = Text.transform(PMB.text(element))

                # Split text into sentences, transform text and add to sections
                sections.extend([(name, x) for x in sent_tokenize(text)])

        return sections

    @staticmethod
    def background(name):
        """
        Checks if the input section name is a background category.

        Args:
            name: section name

        Returns:
            True if the section name is a background category
        """

        return [
            x
            for x in ["aim", "introduction", "background", "purpose", "objective"]
            if x in name.lower()
        ]

    @staticmethod
    def section(name):
        """
        Formats a section name.

        Args:
            name: input section name

        Returns:
            formatted section name
        """

        return re.sub(r"[^\w)]+$", "", name.strip()).upper()
