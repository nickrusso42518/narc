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
    for host, mresult in aresult.items():
        if mresult[0].result:
            print("Error: at least one check is invalid")
            for chk in mresult[0].result:
                name = chk.get("id", "no_id")
                print(f"{host[:12]:<12} {name[:24]:<24} -> {chk['reason']}")
            print("Error: at least one check is invalid")
            sys.exit(1)


if __name__ == "__main__":
    # Use argparse to account for various command line options (-d and -f)
    PARSER = argparse.ArgumentParser()
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
