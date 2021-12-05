"""
SQLite module
"""

import os
import sqlite3

from dateutil import parser

from .database import Database


class SQLite(Database):
    """
    Defines data structures and methods to store article content in SQLite.
    """

    # Articles schema
    ARTICLE = (
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

    # Articles schema
    ARTICLES = {
        "Id": "TEXT PRIMARY KEY",
        "Source": "TEXT",
        "Published": "DATETIME",
        "Publication": "TEXT",
        "Authors": "TEXT",
        "Affiliations": "TEXT",
        "Affiliation": "TEXT",
        "Title": "TEXT",
        "Tags": "TEXT",
        "Reference": "TEXT",
        "Entry": "DATETIME",
    }

    # Sections schema
    SECTIONS = {
        "Id": "INTEGER PRIMARY KEY",
        "Article": "TEXT",
        "Name": "TEXT",
        "Text": "TEXT",
    }

    # SQL statements
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
    INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"
    CREATE_INDEX = "CREATE INDEX section_article ON sections(article)"

    # Restore index when updating an existing database
    SECTION_COUNT = "SELECT MAX(Id) FROM sections"

    # Lookup entry date for an article
    LOOKUP_ENTRY = "SELECT Entry FROM articles WHERE id = ?"

    # Delete article
    DELETE_ARTICLE = "DELETE FROM articles WHERE id = ?"
    DELETE_SECTIONS = "DELETE FROM sections WHERE article = ?"

    def __init__(self, outdir, replace):
        """
        Creates and initializes a new output SQLite database.

        Args:
            outdir: output directory
            replace: If database should be recreated
        """

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        # Output database file
        dbfile = os.path.join(outdir, "articles.sqlite")

        # Create flag
        create = replace or not os.path.exists(dbfile)

        # Delete existing file if replace set
        if replace and os.path.exists(dbfile):
            os.remove(dbfile)

        # Index fields
        self.aindex, self.sindex = 0, 0

        # Connect to output database
        self.db = sqlite3.connect(dbfile)

        # Create database cursor
        self.cur = self.db.cursor()

        if create:
            # Create articles table
            self.create(SQLite.ARTICLES, "articles")

            # Create sections table
            self.create(SQLite.SECTIONS, "sections")

            # Create articles index for sections table
            self.execute(SQLite.CREATE_INDEX)
        else:
            # Restore section index id
            self.sindex = int(self.cur.execute(SQLite.SECTION_COUNT).fetchone()[0]) + 1

        # Start transaction
        self.cur.execute("BEGIN")

    def save(self, article):
        # Save article if not a duplicate
        if self.savearticle(article):
            # Increment number of articles processed
            self.aindex += 1
            if self.aindex % 1000 == 0:
                print(f"Inserted {self.aindex} articles", end="\r")

                # Commit current transaction and start a new one
                self.transaction()

            for name, text in article.sections:
                # Section row - id, article, name, text
                self.insert(
                    SQLite.SECTIONS,
                    "sections",
                    (self.sindex, article.uid(), name, text),
                )
                self.sindex += 1

    def savearticle(self, article):
        """
        Saves an article to SQLite. If a duplicate entry is found, this method compares the entry
        date and keeps the article with the latest entry date.

        Args:
            article: article metadata and text content

        Returns
            True if article saved, False otherwise
        """

        try:
            # Article row
            self.insert(SQLite.ARTICLES, "articles", article.metadata)
        except sqlite3.IntegrityError:
            # Duplicate detected get entry date to determine action
            entry = parser.parse(
                self.cur.execute(SQLite.LOOKUP_ENTRY, [article.uid()]).fetchone()[0]
            )

            # Keep existing article if existing entry date is same or newer
            if article.entry() <= entry:
                return False

            # Delete and re-insert article
            self.cur.execute(SQLite.DELETE_ARTICLE, [article.uid()])
            self.cur.execute(SQLite.DELETE_SECTIONS, [article.uid()])
            self.insert(SQLite.ARTICLES, "articles", article.metadata)

        return True

    def complete(self):
        print(f"Total articles inserted: {self.aindex}")

    def close(self):
        self.db.commit()
        self.db.close()

    def transaction(self):
        """
        Commits current transaction and creates a new one.
        """

        self.db.commit()
        self.cur.execute("BEGIN")

    def create(self, table, name):
        """
        Creates a SQLite table.

        Args:
            table: table schema
            name: table name
        """

        columns = [f"{name} {ctype}" for name, ctype in table.items()]
        create = SQLite.CREATE_TABLE.format(table=name, fields=", ".join(columns))

        # pylint: disable=W0703
        self.cur.execute(create)

    def execute(self, sql):
        """
        Executes SQL statement against open cursor.

        Args:
            sql: SQL statement
        """

        self.cur.execute(sql)

    def insert(self, table, name, row):
        """
        Builds and inserts a row.

        Args:
            table: table object
            name: table name
            row: row to insert
        """

        # Build insert prepared statement
        columns = [name for name, _ in table.items()]
        insert = SQLite.INSERT_ROW.format(
            table=name, columns=", ".join(columns), values=("?, " * len(columns))[:-2]
        )

        # Execute insert statement
        self.cur.execute(insert, self.values(table, row, columns))

    def values(self, table, row, columns):
        """
        Formats and converts row into database types based on table schema.

        Args:
            table: table schema
            row: row tuple
            columns: column names

        Returns:
            Database schema formatted row tuple
        """

        values = []
        for x, column in enumerate(columns):
            # Get value
            value = row[x]

            if table[column].startswith("INTEGER"):
                values.append(int(value) if value else 0)
            elif table[column].startswith("BOOLEAN"):
                values.append(1 if value == "TRUE" else 0)
            elif table[column].startswith("TEXT"):
                # Clean empty text and replace with None
                values.append(value if value and len(value.strip()) > 0 else None)
            else:
                values.append(value)

        return values
