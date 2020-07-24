"""
Table module
"""

import re

from lxml import etree

class Table(object):
    """
    Parses text content from HTML tables.
    """

    @staticmethod
    def parse(text):
        """
        Parses content from a HTML table string. Builds a list of header-value pairs for each row.

        Args:
            text: HTML table string

        Returns:
            list of header-value pairs for each row
        """

        # Parse HTML content using lxml
        # pylint: disable=c-extension-no-member
        table = etree.HTML(text).find("body/table")

        return Table.extract(table)

    @staticmethod
    def extract(table):
        """
        Parses content from a HTML table element. Builds a list of header-value pairs for each row.

        Args:
            table: HTML table element

        Returns:
            list of header-value pairs for each row
        """

        # Table rows
        output = []

        if len(table) > 0:
            rows = iter(table)
            headers = [col.text for col in next(rows)]

            for row in rows:
                # Build concatenated header value string
                values = ["%s %s" % (headers[x] if x < len(headers) else "", column.text) for x, column in enumerate(row)]

                # Create single row string
                value = " ".join(values)

                # Remove whitespace
                value = re.sub(r"[\n\xa0\t]|\s{2,}", " ", value).strip()
                if value:
                    output.append(value)

        return output
