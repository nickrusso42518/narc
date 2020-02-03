#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define custom Nornir tasks for use with the main runbook.
"""

import os
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_json, load_yaml
from narc.helpers import validate_checks, get_cmd, status


def run_checks(task, args):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs via netmiko, and record results.
    Returns a list of strings containing each command issued in sequence.
    """

    # Load the checks for each inventory host
    checks = _load_checks(task, args)

    # Validate the checks. If any fail, quit early and return the failures
    fail_checks = validate_checks(checks)
    if len(fail_checks) > 0:
        return fail_checks

    # Iterate over the user-supplied checks
    total = len(checks)
    for i, chk in enumerate(checks):

        # Store the current item and print a starting status message
        item = chk["id"]
        status(args.status, task, f"starting  check {item} ({i+1}/{total})")

        # If dryrun, use the mock task (regression testing only)
        if args.dryrun:
            task.run(task=_mock_packet_trace, chk=chk)

        # Else, it's a live run, assemble the packet-tracer command
        # and send to the ASA using netmiko. If the individual host
        # has defined Netmiko minor options, include them
        else:
            cmd = get_cmd(chk)
            task.run(
                task=netmiko_send_command,
                command_string=cmd,
                expect_string=task.host.get("netmiko_expect_string"),
                delay_factor=task.host.get("netmiko_delay_factor", 1),
            )

        # Print a completed status message
        status(args.status, task, f"completed check {item} ({i+1}/{total})")

    # Nornir handles this by default, but being explicit makes logic easier
    return None


def _load_checks(task, args):
    """
    Loads in host-specific variables from JSON (primary) or YAML
    (secondary) files from the 'host_vars/' directory.
    """

    # Attempt to variables from JSON first, then YAML.
    # If neither are present, raise a FileNotFoundError
    file_base = f"host_vars/{task.host.name}"
    if os.path.exists(f"{file_base}.json"):
        status(args.status, task, "loading JSON vars")
        check_result = task.run(task=load_json, file=f"{file_base}.json")
    elif os.path.exists(f"{file_base}.yaml"):
        status(args.status, task, "loading YAML vars")
        check_result = task.run(task=load_yaml, file=f"{file_base}.yaml")
    else:
        status(args.status, task, "no JSON/YAML vars file")
        raise FileNotFoundError(f"{file_base} json/yaml file missing")

    # Extract the "checks" list from inside the Result/MR objects
    status(args.status, task, "loading vars succeeded")
    return check_result[0].result["checks"]


def _mock_packet_trace(task, chk):
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
    return xml_text + "</result>"
