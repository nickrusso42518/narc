#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define unit tests for the helper validation functions.
"""

import pytest
import yaml
import modules.helpers as h


@pytest.fixture(scope="module")
def cmd_checks():
    """
    Test fixture setup to load in the relevant test data
    """
    with open("tests/cmd_checks.yaml", "r") as handle:
        checks = yaml.safe_load(handle)
    return checks["cmd_checks"]


def test_get_cmd_tcp(cmd_checks):
    """
    Test the "get_cmd" function on TCP-based checks.
    """
    expected_cmd = "packet-tracer input inside tcp 192.0.2.1 5001 192.0.2.2 5002 xml"
    tcp_str = h.get_cmd(cmd_checks["tcp_str"])
    assert tcp_str == expected_cmd

    tcp_int = h.get_cmd(cmd_checks["tcp_int"])
    assert tcp_int == expected_cmd


def test_get_cmd_udp(cmd_checks):
    """
    Test the "get_cmd" function on UDP-based checks.
    """
    expected_cmd = "packet-tracer input inside udp 192.0.2.1 5001 192.0.2.2 5002 xml"
    udp_str = h.get_cmd(cmd_checks["udp_str"])
    assert udp_str == expected_cmd

    udp_int = h.get_cmd(cmd_checks["udp_int"])
    assert udp_int == expected_cmd


def test_get_cmd_icmp(cmd_checks):
    """
    Test the "get_cmd" function on ICMP-based checks.
    """
    expected_cmd = "packet-tracer input inside icmp 192.0.2.1 8 0 192.0.2.2 xml"
    icmp_str = h.get_cmd(cmd_checks["icmp_str"])
    assert icmp_str == expected_cmd

    icmp_int = h.get_cmd(cmd_checks["icmp_int"])
    assert icmp_int == expected_cmd


def test_get_cmd_other(cmd_checks):
    """
    Test the "get_cmd" function on other numbered IP protocols.
    """
    expected_cmd = "packet-tracer input inside 123 192.0.2.1 192.0.2.2 xml"
    other_int = h.get_cmd(cmd_checks["other_int"])
    assert other_int == expected_cmd
