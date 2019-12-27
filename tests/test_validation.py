#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define unit tests for the helper validation functions.
"""

import pytest
import yaml
import narc.helpers as h


@pytest.fixture(scope="module")
def dummy_checks():
    """
    Test fixture setup to create dummy 'checks' list
    """
    with open("tests/dummy_checks.yaml", "r") as handle:
        checks = yaml.safe_load(handle)
    return checks["dummy_checks"]


def test_validate_id(dummy_checks):
    """
    Test the "validate_id" function.
    """
    fail_list = []
    assert not h.validate_id(dummy_checks["empty_dict"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_id(dummy_checks["blank_id"], fail_list)
    assert "missing" in fail_list[1]["reason"]
    assert h.validate_id(dummy_checks["valid_id"], fail_list)
    assert len(fail_list) == 2


def test_validate_in_intf(dummy_checks):
    """
    Test the "validate_in_intf" function.
    """
    fail_list = []
    assert not h.validate_in_intf(dummy_checks["empty_dict"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_in_intf(dummy_checks["blank_in_intf"], fail_list)
    assert "missing" in fail_list[1]["reason"]
    assert h.validate_in_intf(dummy_checks["valid_in_intf"], fail_list)
    assert len(fail_list) == 2


def test_validate_should(dummy_checks):
    """
    Test the "validate_should" function.
    """
    fail_list = []
    assert not h.validate_should(dummy_checks["empty_dict"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_should(dummy_checks["invalid_should"], fail_list)
    assert "value must be allow|drop" in fail_list[1]["reason"]
    assert h.validate_should(dummy_checks["valid_should"], fail_list)
    assert len(fail_list) == 2


def test_validate_ip(dummy_checks):
    """
    Test the "validate_ip" function.
    """
    fail_list = []
    assert not h.validate_ip(dummy_checks["missing_src_ip"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_ip(dummy_checks["missing_dst_ip"], fail_list)
    assert "missing" in fail_list[1]["reason"]
    assert not h.validate_ip(dummy_checks["invalid_ip"], fail_list)
    assert "must be a v4 or v6 addr" in fail_list[2]["reason"]
    assert not h.validate_ip(dummy_checks["mismatch_ip_ver"], fail_list)
    assert "version mismatch" in fail_list[3]["reason"]
    assert not h.validate_ip(dummy_checks["duplicate_ipv4"], fail_list)
    assert "cannot be the same addr" in fail_list[4]["reason"]
    assert not h.validate_ip(dummy_checks["duplicate_ipv6"], fail_list)
    assert "cannot be the same addr" in fail_list[5]["reason"]
    assert h.validate_ip(dummy_checks["valid_ipv4"], fail_list)
    assert h.validate_ip(dummy_checks["valid_ipv6"], fail_list)
    assert len(fail_list) == 6


def test_validate_proto(dummy_checks):
    """
    Test the "validate_proto" function.
    """
    fail_list = []
    assert not h.validate_proto(dummy_checks["empty_dict"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_proto(dummy_checks["invalid_proto_int"], fail_list)
    assert "int must be 0-255" in fail_list[1]["reason"]
    assert not h.validate_proto(dummy_checks["invalid_proto_str"], fail_list)
    assert "string must be tcp|udp|icmp" in fail_list[2]["reason"]
    assert h.validate_proto(dummy_checks["valid_proto_int"], fail_list)
    assert h.validate_proto(dummy_checks["valid_proto_str"], fail_list)
    assert len(fail_list) == 3


def test_validate_port(dummy_checks):
    """
    Test the "validate_port" function.
    """
    fail_list = []
    assert not h.validate_port(dummy_checks["missing_src_port"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_port(dummy_checks["missing_dst_port"], fail_list)
    assert "missing" in fail_list[1]["reason"]
    assert not h.validate_port(dummy_checks["invalid_port"], fail_list)
    assert "must be int 0-65535" in fail_list[2]["reason"]
    assert h.validate_port(dummy_checks["valid_port"], fail_list)
    assert len(fail_list) == 3


def test_validate_icmp(dummy_checks):
    """
    Test the "validate_icmp" function.
    """
    fail_list = []
    assert not h.validate_icmp(dummy_checks["missing_icmp_type"], fail_list)
    assert "missing" in fail_list[0]["reason"]
    assert not h.validate_icmp(dummy_checks["missing_icmp_code"], fail_list)
    assert "missing" in fail_list[1]["reason"]
    assert not h.validate_icmp(dummy_checks["invalid_icmp_type"], fail_list)
    assert "must be int 0-255" in fail_list[2]["reason"]
    assert not h.validate_icmp(dummy_checks["invalid_icmp_code"], fail_list)
    assert "must be int 0-255" in fail_list[3]["reason"]
    assert h.validate_icmp(dummy_checks["valid_icmp"], fail_list)
    assert len(fail_list) == 4
