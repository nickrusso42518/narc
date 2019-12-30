#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Trivial JSON linter to run before connecting to network devices.
"""

import os
import json
import sys


def main():
    """
    Find all JSON files and ensure they are formatted correctly.
    """

    path = "host_vars/"
    failed = False

    # For every JSON file ...
    for varfile in os.listdir(path):
        if varfile.endswith(".json"):
            filepath = os.path.join(path, varfile)
            with open(filepath, "r") as handle:
                try:
                    # Attempt to load the JSON data into Python objects
                    json.load(handle)
                except json.decoder.JSONDecodeError as exc:
                    # Print specific file and error condition, mark failure
                    print(f"{filepath}: {exc}")
                    failed = True

    # If failure occurred, use rc=1 to signal an error
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
