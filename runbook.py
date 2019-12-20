#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import argparse
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_yaml
import style


def run_checks(task):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs via netmiko, and record results.
    Returns a list of strings containing each command issued in sequence.
    """
    checks = task.run(task=load_yaml, file=f"host_vars/{task.host.name}.yaml")

    for chk in checks[0].result["checks"]:
        cmd = (
            "packet-tracer input "
            f"{chk['in_intf']} {chk['proto']} "
            f"{chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
            "xml"
        )
        task.run(task=netmiko_send_command, command_string=cmd)


def main(args):
    """
    Execution begins here.
    """

    # Evaluate args.style to select a styling function (default is terse)
    style_map = {
        "terse": style.style_terse,
        "csv": style.style_csv,
        "json": style.style_json,
    }
    display_result = style_map.get(args.style, style.style_terse)

    # Initialize nornir and invoke the  task.
    nornir = InitNornir()

    # Initialize nornir and invoke the custom "run_checks" task
    aresult = nornir.run(task=run_checks)
    display_result(aresult, args.failonly)


if __name__ == "__main__":
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
        help="print failures (should != action) only",
        action="store_true",
    )
    main(PARSER.parse_args())
