"""
Defines main entry point for ETL process.
"""

import sys

from .execute import Execute

if __name__ == "__main__":
    if len(sys.argv) > 2:
        Execute.run(
            sys.argv[1],
            sys.argv[2],
            sys.argv[3] if len(sys.argv) > 3 else None,
            sys.argv[4] == "True" if len(sys.argv) > 4 else False,
        )
