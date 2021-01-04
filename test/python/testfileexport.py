"""
File ETL to JSON/YAML tests
"""

import json
import os

import yaml

# pylint: disable=E0401
from paperetl.file.execute import Execute

from testprocess import TestProcess
from utils import Utils

class TestFileExport(TestProcess):
    """
    File ETL to JSON/YAML tests
    """

    def testJSON(self):
        """
        Test JSON export
        """

        self.export("json")

    def testYAML(self):
        """
        Test YAML export
        """

        self.export("yaml")

    def export(self, method):
        """
        Test a file export.

        Args:
            method: export method (json or yaml)
        """

        # Output directory
        output = Utils.FILE + "/models"

        # Build articles database
        Execute.run(Utils.FILE + "/data", "%s://" % method + output, Utils.STUDY)

        # Count of articles/sections
        articles = 0
        sections = 0

        # Read from JSON output files
        for f in os.listdir(output):
            path = os.path.join(output, f)
            if os.path.isfile(path) and path.endswith(method):
                articles += 1

                with open(path) as ifile:
                    data = yaml.safe_load(ifile) if method == "yaml" else json.load(ifile)
                    sections += len(data["sections"])

        # Validate counts
        self.assertEqual(articles, 10)
        self.assertEqual(sections, 3592)
