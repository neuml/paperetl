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

from ..factory import Factory
from ..schema.article import Article
from .section import Section


class Execute:
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
        return "https://doi.org/" + row["doi"]

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
        keywords = [
            r"2019[\-\s]?n[\-\s]?cov",
            "2019 novel coronavirus",
            "coronavirus 2(?:019)?",
            r"coronavirus disease (?:20)?19",
            r"covid(?:[\-\s]?(?:20)?19)?",
            r"n\s?cov[\-\s]?2019",
            r"sars[\-\s]cov-?2",
            r"wuhan (?:coronavirus|cov|pneumonia)",
        ]

        # Build regular expression for each keyword. Wrap term in word boundaries
        regex = "|".join([f"\\b{keyword.lower()}\\b" for keyword in keywords])

        tags = None
        for _, text in sections:
            # Look for at least one keyword match
            if re.findall(regex, text.lower()):
                tags = "COVID-19"
                break

        return tags

    @staticmethod
    def stream(indir, dates):
        """
        Generator that yields rows from a metadata.csv file. The directory is also included.

        Args:
            indir: input directory
            dates: list of uid - entry dates for current metadata file
        """

        # Filter out duplicate ids
        ids, hashes = set(), set()

        with open(
            os.path.join(indir, "metadata.csv"), mode="r", encoding="utf-8"
        ) as csvfile:
            for row in csv.DictReader(csvfile):
                # cord uid
                uid = row["cord_uid"]

                # sha hash
                sha = Execute.getHash(row)

                # Only process if all conditions below met:
                #  - cord uid in entry date mapping
                #  - cord uid and sha hash not already processed
                if uid in dates and uid not in ids and sha not in hashes:
                    yield (row, indir)

                # Add uid and sha as processed
                ids.add(uid)
                hashes.add(sha)

    @staticmethod
    def process(params):
        """
        Processes a single row

        Args:
            params: (row, indir)

        Returns:
            (id, article, sections)
        """

        # Unpack parameters
        row, indir = params

        # Published date
        date = Execute.getDate(row)

        # Get text sections
        sections = Section.parse(row, indir)

        # Search recent documents for COVID-19 keywords
        tags = (
            Execute.getTags(sections)
            if not date or date >= datetime(2019, 7, 1)
            else None
        )

        # Article metadata - id, source, published, publication, authors, affiliations, affiliation, title,
        #                    tags, reference
        metadata = (
            row["cord_uid"],
            row["source_x"],
            date,
            row["journal"],
            row["authors"],
            None,
            None,
            row["title"],
            tags,
            Execute.getUrl(row),
        )

        return Article(metadata, sections)

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
        with open(entryfile, mode="r", encoding="utf-8") as csvfile:
            for row in csv.DictReader(csvfile):
                entries[row["sha"]] = (row["cord_uid"], row["date"])

        # Reduce down to entries only in metadata
        dates = {}
        with open(
            os.path.join(indir, "metadata.csv"), mode="r", encoding="utf-8"
        ) as csvfile:
            for row in csv.DictReader(csvfile):
                # Lookup hash
                sha = Execute.getHash(row)

                # Lookup record
                uid, date = entries[sha]

                # Store date if cord uid maps to value in entries
                if row["cord_uid"] == uid:
                    dates[uid] = parser.parse(date)

        return dates

    @staticmethod
    def run(indir, url, entryfile=None, replace=False):
        """
        Main execution method.

        Args:
            indir: input directory
            url: database url
            entryfile: path to entry dates file
            replace: if true, a new database will be created, overwriting any existing database
        """

        print(f"Building articles database from {indir}")

        # Create database
        db = Factory.create(url, replace)

        # Load entry dates
        dates = Execute.entryDates(indir, entryfile)

        # Create process pool
        with Pool(os.cpu_count()) as pool:
            for article in pool.imap(
                Execute.process, Execute.stream(indir, dates), 100
            ):
                # Get unique id
                uid = article.uid()

                # Only load untagged rows if this is a full database load
                if article.tags():
                    # Append entry date
                    article.metadata = article.metadata + (dates[uid],)

                    # Save article
                    db.save(article)

            pool.close()
            pool.join()

        # Complete processing
        db.complete()

        # Commit and close
        db.close()
