#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define custom Python functions to assist with Nornir tasks.
These cannot be fed directly into Nornir but can be referenced within
those tasks.
"""

from netaddr import IPAddress
from netaddr.core import AddrFormatError


def validate_checks(checks):
    """
    Perform data validation on the 'checks' list. Returns a list of failed
    checks for further processing (empty list means success)
    """

    fail_list = []
    for chk in checks:

        # Validate various fields for correctness
        if not _validate_id(chk, fail_list):
            continue

        if not _validate_in_intf(chk, fail_list):
            continue

        if not _validate_should(chk, fail_list):
            continue

        if not _validate_ip(chk, fail_list):
            continue

        if not _validate_proto(chk, fail_list):
            continue

        # If proto is tcp/udp, check src/dst port
        if chk["proto"] in ["tcp", "6", "udp", "17"]:
            if not _validate_port(chk, fail_list):
                continue

        # If proto is icmp check type/code
        if chk["proto"] in ["icmp", "1"]:
            if not _validate_icmp(chk, fail_list):
                continue

    # Return list of all failures; empty list means success
    return fail_list


def _validate_id(chk, fail_list):
    if not "id" in chk or not chk["id"]:
        _fail_check(chk, fail_list, "'id' key missing or false-y")
        return False
    return True


def _validate_in_intf(chk, fail_list):
    if not "in_intf" in chk or not chk["in_intf"]:
        _fail_check(chk, fail_list, "'in_intf' key missing or false-y")
        return False
    return True


def _validate_ip(chk, fail_list):
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
    return True


def _validate_should(chk, fail_list):
    if not "should" in chk or chk["should"].lower() not in ["allow", "drop"]:
        _fail_check(chk, fail_list, "'should' key missing or isn't allow/drop")
        return False
    return True


def _validate_proto(chk, fail_list):
    if not "proto" in chk or not chk["proto"]:
        _fail_check(chk, fail_list, "'proto' key missing")
        return False

    try:
        proto_num = int(chk["proto"])
        # Proto is an int; check range
        if proto_num < 0 or proto_num > 255:
            _fail_check(chk, fail_list, f"'proto' int must be 0-255")
            return False

    except ValueError:
        # Proto is not an int (likely string); check string values
        if chk["proto"].lower() not in ["tcp", "udp", "icmp"]:
            _fail_check(chk, fail_list, f"'proto' string must be tcp|udp|icmp")
            return False
    return True


def _validate_port(chk, fail_list):
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


def _validate_icmp(chk, fail_list):
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
    cmd = f"packet-tracer input {chk['in_intf']} {chk['proto']} "

    # Check for TCP (6) or UDP (17)
    if proto in ["tcp", "6", "udp", "17"]:
        cmd += (
            f"{chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
        )

    # Check for ICMP (1)
    elif proto in ["icmp", "1"]:
        cmd += (
            f"{chk['src_ip']} {chk['icmp_type']} "
            f"{chk['icmp_code']} {chk['dst_ip']} "
        )

    # Protocol is an uncommon protocol specified numerically
    else:
        cmd += f"{chk['src_ip']} {chk['dst_ip']} "

    # Append "xml" to the command string to specify XML output format
    return cmd + "xml"
