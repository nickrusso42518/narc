#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define unit tests for the helper validation functions.
"""

import pytest
import yaml
import narc.helpers as h


@pytest.fixture(scope="module")
def cmd_checks():
    """
    Test fixture setup to load in the relevant test data
    """
    with open("tests/data/cmd_checks.yaml", "r") as handle:
        checks = yaml.safe_load(handle)
    return checks["cmd_checks"]


def test_get_cmd_tcp(cmd_checks):
    """
    Test the "get_cmd" function on TCP-based checks.
    """
    expected_cmd = "packet-tracer input inside tcp 192.0.2.1 5001 192.0.2.2 5002 xml"
    tcp_full = h.get_cmd(cmd_checks["tcp_full"])
    assert tcp_full == expected_cmd


def test_get_cmd_udp(cmd_checks):
    """
    Test the "get_cmd" function on UDP-based checks.
    """
    expected_cmd = "packet-tracer input inside udp 192.0.2.1 5001 192.0.2.2 5002 xml"
    udp_full = h.get_cmd(cmd_checks["udp_full"])
    assert udp_full == expected_cmd


def test_get_cmd_icmp(cmd_checks):
    """
    Test the "get_cmd" function on ICMP-based checks.
    """
    expected_cmd = "packet-tracer input inside icmp 192.0.2.1 8 0 192.0.2.2 xml"
    icmp_full = h.get_cmd(cmd_checks["icmp_full"])
    assert icmp_full == expected_cmd


def test_get_cmd_rawip(cmd_checks):
    """
    Test the "get_cmd" function on other numbered IP protocols.
    """
    expected_cmd = "packet-tracer input inside rawip 192.0.2.1 123 192.0.2.2 xml"
    rawip_full = h.get_cmd(cmd_checks["rawip_full"])
    assert rawip_full == expected_cmd
