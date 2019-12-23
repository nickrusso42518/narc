#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define custom Nornir tasks for use with the main runbook.
"""

import os
from netaddr import IPAddress
from netaddr.core import AddrFormatError
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_json, load_yaml


def load_checks(task):
    """
    Loads in host-specific variables from JSON (primary) or YAML
    (secondary) files from the 'host_vars/' directory.
    """

    # Attempt to variables from JSON first, then YAML.
    # If neither are present, raise a FileNotFoundError
    file_base = f"host_vars/{task.host.name}"
    if os.path.exists(f"{file_base}.json"):
        data = task.run(task=load_json, file=f"{file_base}.json")
    elif os.path.exists(f"{file_base}.yaml"):
        data = task.run(task=load_yaml, file=f"{file_base}.yaml")
    else:
        raise FileNotFoundError(f"{file_base} json/yaml file missing")


def validate_checks(task, load_ar):
    """
    Perform data validation on the 'checks' list.
    """

    # IP addresses are valid IPv4 or IPv6, and not mixed within a single rule
    # names are unique (they are keys in JSON format and differentiators in terse format)
    fail_list = []
    for chk in load_ar[task.host.name][1].result["checks"]:
        # Ensure required fields are present
        for req_field in ["id", "proto", "in_intf", "src_ip", "dst_ip", "should"]:
            _validate_check(
                req_field not in chk,
                chk,
                fail_list,
                f"missing '{req_field}', always required",
            )

        # If source IP exists, make sure it is a valid IPv4/IPv6 address
        src_ip = None
        src_ip_str = chk.get("src_ip")
        if src_ip_str is not None:
            try:
                src_ip = IPAddress(src_ip_str)
            except AddrFormatError:
                breakpoint()
                _validate_check(
                    True,
                    chk,
                    fail_list,
                    "'src_ip' must be a valid IPv4 or IPv6 address string",
                )

        # If destination IP exists, make sure it is a valid IPv4/IPv6 address
        dst_ip = None
        dst_ip_str = chk.get("dst_ip")
        if dst_ip_str is not None:
            try:
                dst_ip = IPAddress(dst_ip_str)
            except AddrFormatError:
                _validate_check(
                    True,
                    chk,
                    fail_list,
                    "'dst_ip' must be a valid IPv4 or IPv6 address string",
                )

        # Ensure IP addresses are the same version
        if dst_ip is not None and src_ip is not None:
            _validate_check(
                src_ip.version != dst_ip.version,
                chk,
                fail_list,
                "'src_ip' and 'dst_ip' must be same version (v4 or v6)",
            )

        # Ensure proto is valid
        try:
            proto_num = int(chk["proto"])
            # Proto is an int; check range
            _validate_check(
                proto_num < 0 or proto_num > 255,
                chk,
                fail_list,
                f"'proto' must be int 0-255 or ['tcp', 'udp', 'icmp']",
            )
        except ValueError:
            # Proto is not an int (likely string); check string values
            _validate_check(
                chk["proto"].lower() not in ["tcp", "udp", "icmp"],
                chk,
                fail_list,
                f"'proto' must be int 0-255 or ['tcp', 'udp', 'icmp']",
            )

        # Ensure "should" is a valid action (allow or drop)
        should_str = chk.get("should")
        if should_str is not None:
            _validate_check(
                should_str.lower() not in ["allow", "drop"],
                chk,
                fail_list,
                f"'should' must be 'allow' or 'drop'",
            )

        # Perform TCP/UDP-specific validation
        if chk["proto"] in ["tcp", "6", "udp", "17"]:
            # Ensure TCP/UDP checks specify a source/destination port
            for req_field in ["src_port", "dst_port"]:
                _validate_check(
                    req_field not in chk,
                    chk,
                    fail_list,
                    f"missing '{req_field}', required for TCP/UDP",
                )

                # Ports are defined; now ensure the values are valid
                if req_field in chk:
                    try:
                        port_num = int(chk[req_field])
                    except ValueError:
                        port_num = None

                    _validate_check(
                        port_num is None or port_num < 0 or port_num > 65535,
                        chk,
                        fail_list,
                        f"Invalid '{req_field}', must be integer 0-65535",
                    )

        # Perform ICMP-specific validation
        if chk["proto"] in ["icmp", "1"]:
            # Ensure ICMP checks specify an ICMP type/code
            for req_field in ["icmp_type", "icmp_code"]:
                _validate_check(
                    req_field not in chk,
                    chk,
                    fail_list,
                    f"missing '{req_field}', required for ICMP",
                )
                # Types and codes are defined; now ensure the values are valid
                if req_field in chk:
                    try:
                        icmp_num = int(chk[req_field])
                    except ValueError:
                        icmp_num = None

                    _validate_check(
                        icmp_num is None or icmp_num < 0 or icmp_num > 255,
                        chk,
                        fail_list,
                        f"Invalid '{req_field}', must be integer 0-255",
                    )

    # Return list of all failures; empty list means success
    return fail_list


def _validate_check(fail_condition, chk, fail_list, reason):
    if fail_condition:
        chk.update({"fail_reason": reason})
        fail_list.append(chk)


def run_checks(task, load_ar, dryrun):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs via netmiko, and record results.
    Returns a list of strings containing each command issued in sequence.
    """

    # Iterate over the user-supplied checks
    for chk in load_ar[task.host.name][1].result["checks"]:

        # If dryrun, use the mock task (regression testing only)
        if dryrun:
            task.run(task=_mock_packet_trace, chk=chk)

        # Else, it's a live run, assemble the packet-tracer command
        # and send to the ASA using netmiko
        else:
            cmd = _get_cmd(chk)
            task.run(task=netmiko_send_command, command_string=cmd)


def _get_cmd(chk):
    """
    Assemble the correct "packet-tracer" command based on the "proto"
    value. TCP/UDP use source/destination ports, ICMP uses type/code,
    and other protocols use neither. Returns a valid "packet-tracker"
    command that can be issued to an ASA without further modification.
    """

    proto = str(chk["proto"]).lower()
    cmd = "packet-tracer input "

    # Check for TCP (6) or UDP (17)
    if proto in ["tcp", "6", "udp", "17"]:
        cmd += (
            f"{chk['in_intf']} {chk['proto']} "
            f"{chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
        )

    # Check for ICMP (1)
    elif proto in ["icmp", "1"]:
        cmd += (
            f"{chk['in_intf']} {chk['proto']} "
            f"{chk['src_ip']} {chk['icmp_type']} "
            f"{chk['icmp_code']} {chk['dst_ip']} "
        )

    # Protocol is an uncommon protocol specified numerically
    else:
        cmd += (
            f"{chk['in_intf']} {chk['proto']} " f"{chk['src_ip']} {chk['dst_ip']} "
        )

    # Append "xml" to the command string to specify XML output format
    return cmd + "xml"


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
