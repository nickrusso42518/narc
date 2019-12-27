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
    tcp_full = h.get_cmd(cmd_checks["tcp_full"])
    assert tcp_full == cmd_checks["tcp_full"]["expected_cmd"]


def test_get_cmd_udp(cmd_checks):
    """
    Test the "get_cmd" function on UDP-based checks.
    """
    udp_full = h.get_cmd(cmd_checks["udp_full"])
    assert udp_full == cmd_checks["udp_full"]["expected_cmd"]


def test_get_cmd_icmp(cmd_checks):
    """
    Test the "get_cmd" function on ICMP-based checks.
    """
    icmp_full = h.get_cmd(cmd_checks["icmp_full"])
    assert icmp_full == cmd_checks["icmp_full"]["expected_cmd"]


def test_get_cmd_rawip(cmd_checks):
    """
    Test the "get_cmd" function on other numbered IP protocols.
    """
    rawip_full = h.get_cmd(cmd_checks["rawip_full"])
    assert rawip_full == cmd_checks["rawip_full"]["expected_cmd"]
