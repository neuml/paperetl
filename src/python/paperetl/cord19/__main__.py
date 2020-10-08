"""
Defines main entry point for ETL process.
"""

import sys

from .execute import Execute

if __name__ == "__main__":
    if len(sys.argv) > 1:
        Execute.run(sys.argv[1],
                    sys.argv[2] if len(sys.argv) > 2 else None,
                    sys.argv[3] if len(sys.argv) > 3 else None,
                    sys.argv[4] if len(sys.argv) > 4 else None,
                    sys.argv[5] == "True" if len(sys.argv) > 5 else True,
                    sys.argv[6] if len(sys.argv) > 6 else None)
