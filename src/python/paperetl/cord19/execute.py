"""
Transforms and loads CORD-19 data into an articles database.
"""

import csv
import hashlib
import os.path
import re

from datetime import datetime
from multiprocessing import Pool
from dateutil import parser

from ..analysis import Study
from ..factory import Factory
from ..grammar import Grammar
from ..schema.article import Article
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
    Transforms and loads CORD-19 data into an articles database.
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
    def stream(indir, models, dates, merge):
        """
        Generator that yields rows from a metadata.csv file. The directory is also included.

        Args:
            indir: input directory
            models: models directory
            dates: list of uid - entry dates for current metadata file
            merge: only merges/processes this list of uids, if enabled
        """

        # Filter out duplicate ids
        ids, hashes = set(), set()

        with open(os.path.join(indir, "metadata.csv"), mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                # cord uid
                uid = row["cord_uid"]

                # sha hash
                sha = Execute.getHash(row)

                # Only process if all conditions below met:
                #  - Merge set to None (must check for None as merge can be an empty set) or uid in list of ids to merge
                #  - cord uid in entry date mapping
                #  - cord uid and sha hash not already processed
                if (merge is None or uid in merge) and uid in dates and uid not in ids and sha not in hashes:
                    yield (row, indir, models)

                # Add uid and sha as processed
                ids.add(uid)
                hashes.add(sha)

    @staticmethod
    def process(params):
        """
        Processes a single row

        Args:
            params: (row, indir, models)

        Returns:
            (id, article, sections)
        """

        # Get grammar handle
        grammar = getGrammar()

        # Unpack parameters
        row, indir, models = params

        # Published date
        date = Execute.getDate(row)

        # Get text sections
        sections = Section.parse(row, indir)

        # Search recent documents for COVID-19 keywords
        tags = Execute.getTags(sections) if not date or date >= datetime(2019, 7, 1) else None

        if tags:
            # Build NLP tokens for sections
            tokenslist = grammar.parse([text for _, text in sections])

            # Join NLP tokens with sections
            sections = [(name, text, tokenslist[x]) for x, (name, text) in enumerate(sections)]

            # Parse study design fields
            design, size, sample, method, labels = Study.parse(sections, models)

            # Add additional fields to each section
            sections = [(name, text, labels[x] if labels[x] else grammar.label(tokens)) for x, (name, text, tokens) in enumerate(sections)]
        else:
            # Untagged section, create None default placeholders
            design, size, sample, method = None, None, None, None

            # Extend sections with empty columns
            sections = [(name, text, None) for name, text in sections]

        # Article metadata - id, source, published, publication, authors, title, tags, design, sample size
        #                    sample section, sample method, reference
        metadata = (row["cord_uid"], row["source_x"], date, row["journal"], row["authors"], row["title"], tags, design, size,
                    sample, method, Execute.getUrl(row))

        return Article(metadata, sections, None)

    @staticmethod
    def entryDates(indir, entryfile):
        """
        Loads an entry date lookup file into memory.

        Args:
            indir: input directory
            entryfile: path to entry dates file

        Returns:
            dict of cord uid -> entry date
        """

        # sha - (cord uid, date) mapping
        entries = {}

        # Default path to entry files if not provided
        if not entryfile:
            entryfile = os.path.join(indir, "entry-dates.csv")

        # Load in memory date lookup
        with open(entryfile, mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                entries[row["sha"]] = (row["cord_uid"], row["date"])

        # Reduce down to entries only in metadata
        dates = {}
        with open(os.path.join(indir, "metadata.csv"), mode="r") as csvfile:
            for row in csv.DictReader(csvfile):
                # Lookup hash
                sha = Execute.getHash(row)

                # Lookup record
                uid, date = entries[sha]

                # Store date if cord uid maps to value in entries
                if row["cord_uid"] == uid:
                    dates[uid] = date

        return dates

    @staticmethod
    def run(indir, url, models, entryfile, full, merge):
        """
        Main execution method.

        Args:
            indir: input directory
            url: database url
            models: model directory
            entryfile: path to entry dates file
            full: full database load if True, only loads tagged articles if False
            merge: database url to use for merging prior results
        """

        print("Building articles database from {}".format(indir))

        # Set database url and models defaults if not provided
        if not url:
            url = os.path.join(os.path.expanduser("~"), ".cord19", "models")
            models = url

        # Create database
        db = Factory.create(url)

        # Load entry dates
        dates = Execute.entryDates(indir, entryfile)

        # Merge existing db, if present
        if merge:
            merge = db.merge(merge, dates)
            print("Merged results from existing articles database")

        # Create process pool
        with Pool(os.cpu_count()) as pool:
            for article in pool.imap(Execute.process, Execute.stream(indir, models, dates, merge), 100):
                # Get unique id
                uid = article.uid()

                # Only load untagged rows if this is a full database load
                if full or article.tags():
                    # Append entry date
                    article.metadata = article.metadata + (dates[uid],)

                    # Save article
                    db.save(article)

        # Complete processing
        db.complete()

        # Commit and close
        db.close()
