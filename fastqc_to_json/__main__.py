#!/usr/bin/env python
"""
Python Project Template Entrypoint Script
"""

import datetime
import logging
import sys

import click
from .main import main

try:
    from fastqc_to_json import __version__
except Exception:
    __version__ = '0.0.0'

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s:%(lineno)s %(levelname)s | %(message)s",
)


def main() -> int:
    """Main Entrypoint."""
    exit_code = 0
    args = sys.argv

    log.info("Version: %s", __version__)
    log.info("Process called with %s", args)

    try:
        exit_code = sys.exit(main())
    except Exception as e:
        log.exception(e)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    """CLI Entrypoint"""

    status_code = 0
    try:
        status_code = main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)
    sys.exit(status_code)


# __END__
