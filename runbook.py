#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import argparse
import json
import sys
from nornir import InitNornir
from style import process_result
from tasks import load_checks, validate_checks, run_checks


def main(args):
    """
    Execution begins here.
    """

    # Initialize nornir using default configuration settings
    nornir = InitNornir()

    # Load host variables in, which is a list of dictionaries (checks)
    load_ar = nornir.run(task=load_checks)

    # Validate the checks by passing in the previous result
    validate_ar = nornir.run(task=validate_checks, load_ar=load_ar)

    # Check each host to see if any checks were invalid
    fail_dict = {}
    for host, validate_mr in validate_ar.items():
        if len(validate_mr[0].result) > 0:
            fail_dict.update({host: validate_mr[0].result})

    # If there were any failures, exit with code 1 to signal invalid input
    if len(fail_dict) > 0:
        print(json.dumps(fail_dict, indent=2), file=sys.stderr)
        sys.exit(1)

    # All checks are good; execute them by passing in the previous result
    run_ar = nornir.run(task=run_checks, load_ar=load_ar, dryrun=args.dryrun)

    # Call the process_result method passing in the nornir AggregatedResult
    # failonly Boolean, and style type
    overall_success = process_result(load_ar, run_ar, args.failonly, args.style)

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
