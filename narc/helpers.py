#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define custom Python functions to assist with Nornir tasks.
These cannot be fed directly into Nornir but can be referenced within
those tasks.
"""

from datetime import datetime
from netaddr import IPAddress
from netaddr.core import AddrFormatError


def status(condition, task, msg):
    """
    Print the supplied message when the condition is true using
    the following format:
      {hostname}@{utc_timestamp}: {msg}
    """
    if condition:
        time = datetime.utcnow().isoformat()
        print(f"{task.host.name}@{time}: {msg}")


def validate_checks(checks):
    """
    Perform data validation on the 'checks' list. Returns a list of failed
    checks for further processing (empty list means success)
    """

    fail_list = []
    unique_id_set = set()
    for chk in checks:

        # Validate various fields for correctness
        if not validate_id(chk, fail_list):
            continue

        # The 'id' is known good; add to a set
        unique_id_set.add(chk["id"])

        if not validate_in_intf(chk, fail_list):
            continue

        if not validate_should(chk, fail_list):
            continue

        if not validate_ip(chk, fail_list):
            continue

        if not validate_proto(chk, fail_list):
            continue

        # If proto is tcp/udp, check src/dst port
        if chk["proto"] in ["tcp", "6", "udp", "17"]:
            if not validate_port(chk, fail_list):
                continue

        # If proto is icmp check type/code
        if chk["proto"] in ["icmp", "1"]:
            if not validate_icmp(chk, fail_list):
                continue

    # Finally, ensure there are no duplicate IDs
    if len(unique_id_set) < len(checks):
        _fail_check(checks[0], fail_list, "found duplicate id; review all checks")

    # Return list of all failures; empty list means success
    return fail_list


def validate_id(chk, fail_list):
    """
    Ensure the "id" key in the "check" dictionary is present
    and valid. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    if not "id" in chk or not chk["id"]:
        _fail_check(chk, fail_list, "'id' key missing or false-y")
        return False
    return True


def validate_in_intf(chk, fail_list):
    """
    Ensure the "in_intf" key in the "check" dictionary is present
    and valid. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    if not "in_intf" in chk or not chk["in_intf"]:
        _fail_check(chk, fail_list, "'in_intf' key missing or false-y")
        return False
    return True


def validate_ip(chk, fail_list):
    """
    Ensure the "src_ip" and "dst_ip" keys in the "check" dictionary are
    present and valid. Must be properly formatted IPv4 or IPv6 address for
    both source and dest IPs. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    ip_list = []
    for ip_key in ["src_ip", "dst_ip"]:
        if not ip_key in chk:
            _fail_check(chk, fail_list, f"'{ip_key}' key missing")
            return False

        try:
            ip_list.append(IPAddress(chk[ip_key]))
        except AddrFormatError:
            _fail_check(chk, fail_list, f"'{ip_key}' must be a v4 or v6 addr")
            return False

    if ip_list[0].version != ip_list[1].version:
        _fail_check(chk, fail_list, "src/dst ip version mismatch (v4 or v6)")
        return False

    if ip_list[0] == ip_list[1]:
        _fail_check(chk, fail_list, "src/dst ip cannot be the same addr")
        return False
    return True


def validate_should(chk, fail_list):
    """
    Ensure the "should" key in the "check" dictionary is
    present and valid. Must be "allow" or "drop"; no other value.
    Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    if not "should" in chk:
        _fail_check(chk, fail_list, "'should' key missing")
        return False
    if chk["should"].lower() not in ["allow", "drop"]:
        _fail_check(chk, fail_list, "'should' value must be allow|drop")
        return False
    return True


def validate_proto(chk, fail_list):
    """
    Ensure the "should" key in the "check" dictionary is
    present and valid. Must be "tcp", "udp", or "icmp" as a string,
    or an integer 0-255. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    if not "proto" in chk or not chk["proto"]:
        _fail_check(chk, fail_list, "'proto' key missing or false-y")
        return False

    try:
        proto_num = int(chk["proto"])
        # Proto is an int; check range
        if proto_num < 0 or proto_num > 255:
            _fail_check(chk, fail_list, "'proto' int must be 0-255")
            return False

    except ValueError:
        # Proto is not an int (likely string); check string values
        if chk["proto"].lower() not in ["tcp", "udp", "icmp"]:
            _fail_check(chk, fail_list, "'proto' string must be tcp|udp|icmp")
            return False
    return True


def validate_port(chk, fail_list):
    """
    Ensure the "src_port" and "dst_port" keys in the "check" dictionary are
    present and valid. Must be integers between 0 and 65535; relevant only for
    TCP or UDP checks. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    for key in ["src_port", "dst_port"]:
        if key not in chk:
            _fail_check(chk, fail_list, f"missing tcp/udp '{key}' key")
            return False

        try:
            val = int(chk[key])
            if val < 0 or val > 65535:
                raise ValueError
        except ValueError:
            _fail_check(chk, fail_list, f"'{key}' must be int 0-65535")
            return False
    return True


def validate_icmp(chk, fail_list):
    """
    Ensure the "icmp_type" and "icmp_code" keys in the "check" dictionary are
    present and valid. Must be integers between 0 and 255; relevant only for
    ICMP checks. Return False if any condition is not satisfied
    and also append the check to the fail_list with a fail reason.
    """
    for key in ["icmp_type", "icmp_code"]:
        if key not in chk:
            _fail_check(chk, fail_list, f"missing icmp '{key}' key")
            return False

        try:
            val = int(chk[key])
            if val < 0 or val > 255:
                raise ValueError
        except ValueError:
            _fail_check(chk, fail_list, f"'{key}' must be int 0-255")
            return False
    return True


def _fail_check(chk, fail_list, reason):
    """
    Small internal wrapper function that updates the given check with
    the failure "reason" and appends it to the supplied fail_list".
    """
    chk.update({"reason": reason})
    fail_list.append(chk)


def get_cmd(chk):
    """
    Assemble the correct "packet-tracer" command based on the "proto"
    value. TCP/UDP use source/destination ports, ICMP uses type/code,
    and other protocols use neither. Returns a valid "packet-tracker"
    command that can be issued to an ASA without further modification.
    """

    proto = str(chk["proto"]).lower()
    cmd = f"packet-tracer input {chk['in_intf']} "

    # Check for TCP or UDP
    if proto in ["tcp", "udp"]:
        cmd += (
            f"{proto} {chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
        )

    # Check for ICMP
    elif proto == "icmp":
        cmd += (
            f"icmp {chk['src_ip']} {chk['icmp_type']} "
            f"{chk['icmp_code']} {chk['dst_ip']} "
        )

    # Protocol is an uncommon protocol specified numerically
    else:
        cmd += f"rawip {chk['src_ip']} {chk['proto']} {chk['dst_ip']} "

    # Append "xml" to the command string to specify XML output format
    return cmd + "xml"
