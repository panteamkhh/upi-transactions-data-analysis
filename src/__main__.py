"""Allow ``python -m src`` to run the end-to-end analysis pipeline."""

from __future__ import annotations

import sys

from .run_analysis import main

if __name__ == "__main__":
    sys.exit(main())
