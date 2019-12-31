#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Main entrypoint for narc program.
"""

import argparse
import sys
from nornir import InitNornir
from narc.tasks import run_checks
from narc.processors import ProcTerse, ProcCSV, ProcJSON


def main(args):
    """
    Execution begins here.
    """

    # Initialize nornir using default configuration settings
    init_nornir = InitNornir()
    nornir = init_nornir.with_processors([ProcTerse(), ProcCSV(), ProcJSON()])

    # Execute the "run_checks" task to get started, passing in CLI args
    aresult = nornir.run(task=run_checks, args=args)

    # Handle failed checks by printing them out and exiting with rc=1
    failed = False
    for host, mresult in aresult.items():
        if mresult[0].result:
            print(f"{host} error: at least one check is invalid")
            for chk in mresult[0].result:
                name = chk.get("id", "no_id")
                print(f"{host[:12]:<12} {name[:24]:<24} -> {chk['reason']}")
            failed = True

    if failed:
        sys.exit(1)


def _process_args():
    """
    Process command line arguments according to README.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--failonly",
        help="print failures (ie, undesirable results) only",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        help="run offline system test (no devices needed)",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--status",
        help="log timestamped status messages during runtime",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(_process_args())
