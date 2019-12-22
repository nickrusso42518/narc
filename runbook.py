#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import argparse
import sys
from nornir import InitNornir
from style import process_result
from tasks import run_checks


def main(args):
    """
    Execution begins here.
    """

    # Initialize nornir and invoke the custom "run_checks" task
    nornir = InitNornir()
    aresult = nornir.run(task=run_checks, dryrun=args.dryrun)

    # Call the process_result method passing in the nornir AggregatedResult
    # failonly Boolean, and style type
    overall_success = process_result(aresult, args.failonly, args.style)

    # If any failures occurred, return code 1 to indicate so
    if not overall_success:
        sys.exit(1)


if __name__ == "__main__":
    # Use argparse to account for various command line options (-s and -f)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "-s",
        "--style",
        type=str,
        choices=["terse", "csv", "json"],
        help="output format style",
        default="terse",
    )
    PARSER.add_argument(
        "-f",
        "--failonly",
        help="print failures (ie, undesirable results) only",
        action="store_true",
    )
    PARSER.add_argument(
        "-d",
        "--dryrun",
        help="run offline system test (no devices needed)",
        action="store_true",
    )
    main(PARSER.parse_args())
