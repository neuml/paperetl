"""
Transforms raw CORD-19 data into an articles database.
"""

import csv
import hashlib
import os.path
import re

from collections import Counter
from datetime import datetime
from multiprocessing import Pool
from dateutil import parser

from ..factory import Factory
from ..grammar import Grammar
from ..metadata import Metadata
from .section import Section

# Global helper for multi-processing support
# pylint: disable=W0603
GRAMMAR = None

def getGrammar():
    """
    Multiprocessing helper method. Gets (or first creates then gets) a global grammar object to
    be accessed in a new subprocess.

    Returns:
        Grammar
    """

    global GRAMMAR

    if not GRAMMAR:
        GRAMMAR = Grammar()

    return GRAMMAR

class Execute(object):
    """
    Transforms raw csv/json files and loads into an articles database.
    """

    @staticmethod
    def getHash(row):
        """
        Gets sha hash for this row. Builds one from the title if no body content is available.

        Args:
            row: input row

        Returns:
            sha1 hash id
        """

        # Use sha1 provided, if available
        sha = row["sha"].split("; ")[0] if row["sha"] else None
        if not sha:
            # Fallback to sha1 of title
            sha = hashlib.sha1(row["title"].encode("utf-8")).hexdigest()

        return sha

    @staticmethod
    def getDate(row):
        """
        Parses the publish date from the input row.

        Args:
            row: input row

        Returns:
            publish date
        """

        date = row["publish_time"]

        if date:
            try:
                if date.isdigit() and len(date) == 4:
                    # Default entries with just year to Jan 1
                    date += "-01-01"

                return parser.parse(date)

            # pylint: disable=W0702
            except:
                # Skip parsing errors
                return None

        return None

    @staticmethod
    def getUrl(row):
        """
        Parses the url from the input row.

        Args:
            row: input row

        Returns:
            url
        """

        if row["url"]:
            # Filter out API reference links
            urls = [url for url in row["url"].split("; ") if "https://api." not in url]
            if urls:
                return urls[0]

        # Default to DOI
        return "https://doi.org/"  + row["doi"]

    @staticmethod
    def getTags(sections):
        """
        Searches input sections for matching keywords. If found, returns the keyword tag.

        Args:
            sections: list of text sections

        Returns:
            tags
        """

        # Keyword patterns to search for
        keywords = [r"2019[\-\s]?n[\-\s]?cov", "2019 novel coronavirus", "coronavirus 2(?:019)?", r"coronavirus disease (?:20)?19",
                    r"covid(?:[\-\s]?(?:20)?19)?", r"n\s?cov[\-\s]?2019", r"sars[\-\s]cov-?2", r"wuhan (?:coronavirus|cov|pneumonia)"]

        # Build regular expression for each keyword. Wrap term in word boundaries
        regex = "|".join(["\\b%s\\b" % keyword.lower() for keyword in keywords])

        tags = None
        for _, text in sections:
            # Look for at least one keyword match
            if re.findall(regex, text.lower()):
                tags = "COVID-19"
                break

        return tags

    @staticmethod
    def stream(indir, outdir):
        """
        Generator that yields rows from a metadata.csv file. The directory is also included.

        Args:
            indir: input directory
            outdir: output directory
        """

        with open(os.path.join(indir, "metadata.csv"), mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                yield (row, indir, outdir)

    @staticmethod
    def process(params):
        """
        Processes a single row

        Args:
            params: (row, indir, outdir)

        Returns:
            (id, article, sections)
        """

        # Get grammar handle
        grammar = getGrammar()

        # Unpack parameters
        row, indir, outdir = params

        # Get sha hash
        sha = Execute.getHash(row)

        # Published date
        date = Execute.getDate(row)

        # Get text sections
        sections, citations = Section.parse(row, indir)

        # Search recent documents for COVID-19 keywords
        tags = Execute.getTags(sections) if not date or date >= datetime(2019, 7, 1) else None

        if tags:
            # Build NLP tokens for sections
            tokenslist = grammar.parse([text for _, text in sections])

            # Join NLP tokens with sections
            sections = [(name, text, tokenslist[x]) for x, (name, text) in enumerate(sections)]

            # Derive metadata fields
            design, size, sample, method, labels = Metadata.parse(sections, outdir)

            # Add additional fields to each section
            sections = [(name, text, labels[x] if labels[x] else grammar.label(tokens)) for x, (name, text, tokens) in enumerate(sections)]
        else:
            # Untagged section, create None default placeholders
            design, size, sample, method = None, None, None, None

            # Extend sections with empty columns
            sections = [(name, text, None) for name, text in sections]

            # Clear citations when not a tagged entry
            citations = None

        # Article row - id, source, published, publication, authors, title, tags, design, sample size
        #               sample section, sample method, reference
        article = (row["cord_uid"], row["source_x"], date, row["journal"], row["authors"], row["title"], tags, design, size,
                   sample, method, Execute.getUrl(row))

        return (row["cord_uid"], sha, article, sections, tags, design, citations)

    @staticmethod
    def entryDates(indir, entryfile):
        """
        Loads an entry date lookup file into memory.

        Args:
            indir: input directory
            entryfile: path to entry dates file

        Returns:
            dict of sha id -> entry date
        """

        # Entry date mapping sha id to date
        dates = {}

        # Default path to entry files if not provided
        if not entryfile:
            entryfile = os.path.join(indir, "entry-dates.csv")

        # Load in memory date lookup
        with open(entryfile, mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                dates[row["sha"]] = row["date"]

        return dates

    @staticmethod
    def run(indir, outdir, entryfile, full):
        """
        Main execution method.

        Args:
            indir: input directory
            outdir: output directory
            entryfile: path to entry dates file
            full: full database load if True, only loads tagged articles if False
        """

        print("Building articles database from {}".format(indir))

        # Default output directory if not provided
        if not outdir:
            outdir = os.path.join(os.path.expanduser("~"), ".cord19", "models")

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        # Article, section index, database, processed ids, citations
        db, hashes, citations = Factory.create("sqlite", (outdir,)), set(), Counter()

        # Load entry dates
        dates = Execute.entryDates(indir, entryfile)

        # Create process pool
        with Pool(os.cpu_count()) as pool:
            for uid, sha, article, sections, tags, design, cite in pool.imap(Execute.process, Execute.stream(indir, outdir), 100):
                # Skip rows with hashes that have already been processed
                # Only load untagged rows if this is a full database load
                if sha not in hashes and (full or tags):
                    # Append entry date
                    article = article + (dates[sha],)

                    # Store citation reference
                    citations.update(cite)

                    # Article row
                    db.save(uid, article, sections, tags, design)

                    # Store article hash as processed
                    hashes.add(sha)

        # Complete processing
        db.complete(citations)

        # Commit and close
        db.close()
