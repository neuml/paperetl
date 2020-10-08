"""
SQLite module
"""

import os
import sqlite3

from datetime import datetime, timedelta

from .database import Database

class SQLite(Database):
    """
    Defines data structures and methods to store article content in SQLite.
    """

    # Articles schema
    ARTICLES = {
        "Id": "TEXT PRIMARY KEY",
        "Source": "TEXT",
        "Published": "DATETIME",
        "Publication": "TEXT",
        "Authors": "TEXT",
        "Title": "TEXT",
        "Tags": "TEXT",
        "Design": "INTEGER",
        "Size": "TEXT",
        "Sample": "TEXT",
        "Method": "TEXT",
        "Reference": "TEXT",
        "Entry": "DATETIME"
    }

    # Sections schema
    SECTIONS = {
        "Id": "INTEGER PRIMARY KEY",
        "Article": "TEXT",
        "Tags": "TEXT",
        "Design": "INTEGER",
        "Name": "TEXT",
        "Text": "TEXT",
        "Labels": "TEXT"
    }

    # SQL statements
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
    INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"
    CREATE_INDEX = "CREATE INDEX section_article ON sections(article)"

    # Merge SQL statements
    ATTACH_DB = "ATTACH DATABASE '{path}' as {name}"
    DETACH_DB = "DETACH DATABASE '{name}'"
    MAX_ENTRY = "SELECT MAX(entry) from {name}.articles"
    LOOKUP_ARTICLE = "SELECT Id FROM {name}.articles WHERE Id=? AND Entry = ?"
    MERGE_ARTICLE = "INSERT INTO articles SELECT * FROM {name}.articles WHERE Id = ?"
    MERGE_SECTIONS = "INSERT INTO sections SELECT * FROM {name}.sections WHERE Article=?"
    UPDATE_ENTRY = "UPDATE articles SET entry = ? WHERE Id = ?"
    ARTICLE_COUNT = "SELECT COUNT(1) FROM articles"
    SECTION_COUNT = "SELECT MAX(id) FROM sections"

    def __init__(self, outdir):
        """
        Creates and initializes a new output SQLite database.

        Args:
            outdir: output directory
        """

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        # Output database file
        dbfile = os.path.join(outdir, "articles.sqlite")

        # Delete existing file
        if os.path.exists(dbfile):
            os.remove(dbfile)

        # Index fields
        self.aindex, self.sindex = 0, 0

        # Create output database
        self.db = sqlite3.connect(dbfile)

        # Create database cursor
        self.cur = self.db.cursor()

        # Create articles table
        self.create(SQLite.ARTICLES, "articles")

        # Create sections table
        self.create(SQLite.SECTIONS, "sections")

        # Start transaction
        self.cur.execute("BEGIN")

    def merge(self, url, ids):
        # List of IDs to set for processing
        queue = set()

        # Attached database alias
        alias = "merge"

        # Attach database
        self.db.execute(SQLite.ATTACH_DB.format(path=url, name=alias))

        # Only process records newer than 5 days before the last run
        lastrun = self.cur.execute(SQLite.MAX_ENTRY.format(name=alias)).fetchone()[0]
        lastrun = datetime.strptime(lastrun, "%Y-%m-%d") - timedelta(days=5)
        lastrun = lastrun.strftime("%Y-%m-%d")

        # Search for existing articles
        for uid, date in ids.items():
            self.cur.execute(SQLite.LOOKUP_ARTICLE.format(name=alias), [uid, date])
            if not self.cur.fetchone() and date > lastrun:
                # Add uid to process
                queue.add(uid)
            else:
                # Copy existing record
                self.cur.execute(SQLite.MERGE_ARTICLE.format(name=alias), [uid])
                self.cur.execute(SQLite.MERGE_SECTIONS.format(name=alias), [uid])

                # Sync entry date with ids list
                self.cur.execute(SQLite.UPDATE_ENTRY, [date, uid])

        # Set current index positions
        self.aindex = int(self.cur.execute(SQLite.ARTICLE_COUNT.format(name=alias)).fetchone()[0]) + 1
        self.sindex = int(self.cur.execute(SQLite.SECTION_COUNT.format(name=alias)).fetchone()[0]) + 1

        # Commit transaction
        self.db.commit()

        # Detach database
        self.db.execute(SQLite.DETACH_DB.format(name=alias))

        # Start new transaction
        self.cur.execute("BEGIN")

        # Return list of new/updated ids to process
        return queue

    def save(self, article):
        # Article row
        self.insert(SQLite.ARTICLES, "articles", article.metadata)

        # Increment number of articles processed
        self.aindex += 1
        if self.aindex % 1000 == 0:
            print("Inserted {} articles".format(self.aindex), end="\r")

            # Commit current transaction and start a new one
            self.transaction()

        for name, text, labels in article.sections:
            # Section row - id, article, tags, design, name, text, labels
            self.insert(SQLite.SECTIONS, "sections", (self.sindex, article.uid(), article.tags(), article.design(), name, text, labels))
            self.sindex += 1

    def complete(self):
        print("Total articles inserted: {}".format(self.aindex))

        # Create articles index for sections table
        self.execute(SQLite.CREATE_INDEX)

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

        columns = ["{0} {1}".format(name, ctype) for name, ctype in table.items()]
        create = SQLite.CREATE_TABLE.format(table=name, fields=", ".join(columns))

        # pylint: disable=W0703
        try:
            self.cur.execute(create)
        except Exception as e:
            print(create)
            print("Failed to create table: " + e)

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
        insert = SQLite.INSERT_ROW.format(table=name,
                                          columns=", ".join(columns),
                                          values=("?, " * len(columns))[:-2])

        try:
            # Execute insert statement
            self.cur.execute(insert, self.values(table, row, columns))
        # pylint: disable=W0703
        except Exception as ex:
            print("Error inserting row: {}".format(row), ex)

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
