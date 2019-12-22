#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import argparse
import sys
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_yaml
from style import process_result


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


def run_checks(task, dryrun):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs via netmiko, and record results.
    Returns a list of strings containing each command issued in sequence.
    """
    checks = task.run(task=load_yaml, file=f"host_vars/{task.host.name}.yaml")

    for chk in checks[0].result["checks"]:
        if dryrun:
            task.run(task=mock_packet_trace, chk=chk)
        else:
            cmd = (
                "packet-tracer input "
                f"{chk['in_intf']} {chk['proto']} "
                f"{chk['src_ip']} {chk['src_port']} "
                f"{chk['dst_ip']} {chk['dst_port']} "
                "xml"
            )
            task.run(task=netmiko_send_command, command_string=cmd)


def mock_packet_trace(task, chk):
    """
    Simulates output from a Cisco ASA "packet-tracer" command using XML
    format for local testing. The "result" for all phases, as well as
    the final result, will be set equal to the check["should"] value.
    """

    # Create XML text and substitute "should" for actual result
    result = chk["should"].upper()
    xml_text = f"""
        <Phase>
        <id>1</id>
        <type>ROUTE-LOOKUP</type>
        <subtype>Resolve Egress Interface</subtype>
        <result>{result}</result>
        <config></config>
        <extra>found next-hop 192.0.2.1 using egress ifc  management</extra>
        </Phase>
        <Phase>
        <id>2</id>
        <type>ACCESS-LIST</type>
        <subtype></subtype>
        <result>{result}</result>
        <config>Implicit Rule</config>
        <extra>{task.host.name}</extra>
        </Phase>
        <result>
        <input-interface>UNKNOWN</input-interface>
        <input-status>up</input-status>
        <input-line-status>up</input-line-status>
        <output-interface>UNKNOWN</output-interface>
        <output-status>up</output-status>
        <output-line-status>up</output-line-status>
        <action>{result}</action>
    """

    # If the final result is DROP, append a "drop-reason"
    if result == "DROP":
        xml_text += "<drop-reason>dummy</drop-reason>"

    # Unconditionally append the closing "result" tag
    xml_text += "</result>"
    return xml_text


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
