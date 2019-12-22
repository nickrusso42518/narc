#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define custom Nornir tasks for use with the main runbook.
"""

import os
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_json, load_yaml


def run_checks(task, dryrun):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs via netmiko, and record results.
    Returns a list of strings containing each command issued in sequence.
    """

    # Attempt to variables from JSON first, then YAML.
    # If neither are present, raise a FileNotFoundError
    file_base = f"host_vars/{task.host.name}"
    if os.path.exists(f"{file_base}.json"):
        checks = task.run(task=load_json, file=f"{file_base}.json")
    elif os.path.exists(f"{file_base}.yaml"):
        checks = task.run(task=load_yaml, file=f"{file_base}.yaml")
    else:
        raise FileNotFoundError(f"{file_base} json/yaml missing")

    # Iterate over the user-supplied checks
    for chk in checks[0].result["checks"]:

        # If dryrun, use the mock task (regression testing only)
        if dryrun:
            task.run(task=_mock_packet_trace, chk=chk)

        # Else, it's a live run, assemble the packet-tracer command
        # and send to the ASA using netmiko
        else:
            cmd = (
                "packet-tracer input "
                f"{chk['in_intf']} {chk['proto']} "
                f"{chk['src_ip']} {chk['src_port']} "
                f"{chk['dst_ip']} {chk['dst_port']} "
                "xml"
            )
            task.run(task=netmiko_send_command, command_string=cmd)


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
    xml_text += "</result>"
    return xml_text
