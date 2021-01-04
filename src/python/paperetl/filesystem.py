"""
FileSystem module
"""

import json
import os

import yaml

from .database import Database

class FileSystem(Database):
    """
    Defines data structures and methods to store articles in a filesystem directory.
    """

    def __init__(self, outdir):
        """
        Creates and initializes an output directory to use for writing files.

        Args:
            outdir: output directory
        """

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        self.outdir = outdir

    def save(self, article):
        output = os.path.splitext(article.source if article.source else article.uid())[0] + ".%s" % self.extension()

        with open(os.path.join(self.outdir, output), "w") as output:
            self.write(output, article.build())

    def extension(self):
        """
        Returns file extension for generated files
        """

    def write(self, output, article):
        """
        Writes article content to output stream.

        Args:
            output: output file handle
            article: article object
        """

class JSON(FileSystem):
    """
    Defines data structures and methods to store articles as JSON files.
    """

    def extension(self):
        return "json"

    def write(self, output, article):
        json.dump(article, output, default=str)

class YAML(FileSystem):
    """
    Defines data structures and methods to store articles as YAML files.
    """

    def extension(self):
        return "yaml"

    def write(self, output, article):
        output.write(yaml.safe_dump(article))
