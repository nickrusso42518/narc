#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import argparse
import sys
from nornir import InitNornir
from modules.style import process_result
from modules.tasks import run_checks


def main(args):
    """
    Execution begins here.
    """

    # Initialize nornir using default configuration settings
    nornir = InitNornir()

    # All checks are good; execute them by passing in the previous result
    aresult = nornir.run(task=run_checks, dryrun=args.dryrun)

    # Handle failed checks by printing them out and exiting with rc=1
    for host, mresult in aresult.items():
        if mresult[0].result:
            print("Error: at least one check is invalid")
            for chk in mresult[0].result:
                name = chk["id"] if "id" in chk else "no_id"
                print(f"{host[:12]:<12} {name[:24]:<24} -> {chk['reason']}")
            print("Error: at least one check is invalid")
            sys.exit(1)

    # Call the process_result method passing in the nornir AggregatedResult
    # failonly Boolean, and style type
    overall_success = process_result(aresult, args.failonly, args.style)

    # If any failures occurred, return code 2 to indicate so
    if not overall_success:
        sys.exit(2)


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
