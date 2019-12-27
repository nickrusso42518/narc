#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define unit tests for the helper validation functions.
"""

import pytest
import yaml
import narc.helpers as h


@pytest.fixture(scope="module")
def checks():
    """
    Test fixture setup to create dummy 'checks' list
    """
    with open("tests/data/dummy_checks.yaml", "r") as handle:
        checks = yaml.safe_load(handle)
    return checks["dummy_checks"]


def test_validate_id(checks):
    """
    Test the "validate_id" function.
    """
    fail_list = []
    assert not h.validate_id(checks["missing_id"], fail_list)
    assert "reason" in checks["missing_id"]
    assert fail_list[0]["reason"] == checks["missing_id"]["expected_reason"]
    assert not h.validate_id(checks["blank_id"], fail_list)
    assert "reason" in checks["blank_id"]
    assert fail_list[1]["reason"] == checks["blank_id"]["expected_reason"]
    assert h.validate_id(checks["valid_id"], fail_list)
    assert "reason" not in checks["valid_id"]
    assert len(fail_list) == 2


def test_validate_in_intf(checks):
    """
    Test the "validate_in_intf" function.
    """
    fail_list = []
    assert not h.validate_in_intf(checks["missing_in_intf"], fail_list)
    assert "reason" in checks["missing_in_intf"]
    assert fail_list[0]["reason"] == checks["missing_in_intf"]["expected_reason"]
    assert not h.validate_in_intf(checks["blank_in_intf"], fail_list)
    assert "reason" in checks["blank_in_intf"]
    assert fail_list[1]["reason"] == checks["blank_in_intf"]["expected_reason"]
    assert h.validate_in_intf(checks["valid_in_intf"], fail_list)
    assert "reason" not in checks["valid_in_intf"]
    assert len(fail_list) == 2


def test_validate_should(checks):
    """
    Test the "validate_should" function.
    """
    fail_list = []
    assert not h.validate_should(checks["missing_should"], fail_list)
    assert "reason" in checks["missing_should"]
    assert fail_list[0]["reason"] == checks["missing_should"]["expected_reason"]
    assert not h.validate_should(checks["blank_should"], fail_list)
    assert "reason" in checks["blank_should"]
    assert fail_list[1]["reason"] == checks["blank_should"]["expected_reason"]
    assert not h.validate_should(checks["invalid_should"], fail_list)
    assert "reason" in checks["invalid_should"]
    assert fail_list[2]["reason"] == checks["invalid_should"]["expected_reason"]
    assert h.validate_should(checks["valid_should"], fail_list)
    assert "reason" not in checks["valid_should"]
    assert len(fail_list) == 3


def test_validate_ip(checks):
    """
    Test the "validate_ip" function.
    """
    fail_list = []
    assert not h.validate_ip(checks["missing_src_ip"], fail_list)
    assert "reason" in checks["missing_src_ip"]
    assert fail_list[0]["reason"] == checks["missing_src_ip"]["expected_reason"]

    assert not h.validate_ip(checks["missing_dst_ip"], fail_list)
    assert "reason" in checks["missing_dst_ip"]
    assert fail_list[1]["reason"] == checks["missing_dst_ip"]["expected_reason"]

    assert not h.validate_ip(checks["invalid_ip"], fail_list)
    assert "reason" in checks["invalid_ip"]
    assert fail_list[2]["reason"] == checks["invalid_ip"]["expected_reason"]

    assert not h.validate_ip(checks["mismatch_ip_ver"], fail_list)
    assert "reason" in checks["mismatch_ip_ver"]
    assert fail_list[3]["reason"] == checks["mismatch_ip_ver"]["expected_reason"]

    assert not h.validate_ip(checks["duplicate_ipv4"], fail_list)
    assert "reason" in checks["duplicate_ipv4"]
    assert fail_list[4]["reason"] == checks["duplicate_ipv4"]["expected_reason"]

    assert not h.validate_ip(checks["duplicate_ipv6"], fail_list)
    assert "reason" in checks["duplicate_ipv6"]
    assert fail_list[5]["reason"] == checks["duplicate_ipv6"]["expected_reason"]

    assert h.validate_ip(checks["valid_ipv4"], fail_list)
    assert "reason" not in checks["valid_ipv4"]
    assert h.validate_ip(checks["valid_ipv6"], fail_list)
    assert "reason" not in checks["valid_ipv6"]

    assert len(fail_list) == 6


def test_validate_proto(checks):
    """
    Test the "validate_proto" function.
    """
    fail_list = []
    assert not h.validate_proto(checks["missing_proto"], fail_list)
    assert "reason" in checks["missing_proto"]
    assert fail_list[0]["reason"] == checks["missing_proto"]["expected_reason"]

    assert not h.validate_proto(checks["blank_proto"], fail_list)
    assert "reason" in checks["blank_proto"]
    assert fail_list[1]["reason"] == checks["blank_proto"]["expected_reason"]

    assert not h.validate_proto(checks["invalid_proto_int"], fail_list)
    assert "reason" in checks["invalid_proto_int"]
    assert fail_list[2]["reason"] == checks["invalid_proto_int"]["expected_reason"]

    assert not h.validate_proto(checks["invalid_proto_str"], fail_list)
    assert "reason" in checks["invalid_proto_str"]
    assert fail_list[3]["reason"] == checks["invalid_proto_str"]["expected_reason"]

    assert h.validate_proto(checks["valid_proto_int"], fail_list)
    assert "reason" not in checks["valid_proto_int"]
    assert h.validate_proto(checks["valid_proto_str"], fail_list)
    assert "reason" not in checks["valid_proto_str"]
    assert len(fail_list) == 4


def test_validate_port(checks):
    """
    Test the "validate_port" function.
    """
    fail_list = []
    assert not h.validate_port(checks["missing_src_port"], fail_list)
    assert "reason" in checks["missing_src_port"]
    assert fail_list[0]["reason"] == checks["missing_src_port"]["expected_reason"]

    assert not h.validate_port(checks["missing_dst_port"], fail_list)
    assert "reason" in checks["missing_dst_port"]
    assert fail_list[1]["reason"] == checks["missing_dst_port"]["expected_reason"]

    assert not h.validate_port(checks["invalid_port"], fail_list)
    assert "reason" in checks["invalid_port"]
    assert fail_list[2]["reason"] == checks["invalid_port"]["expected_reason"]

    assert h.validate_port(checks["valid_port"], fail_list)
    assert "reason" not in checks["valid_port"]
    assert len(fail_list) == 3


def test_validate_icmp(checks):
    """
    Test the "validate_icmp" function.
    """
    fail_list = []
    assert not h.validate_icmp(checks["missing_icmp_type"], fail_list)
    assert "reason" in checks["missing_icmp_type"]
    assert fail_list[0]["reason"] == checks["missing_icmp_type"]["expected_reason"]

    assert not h.validate_icmp(checks["missing_icmp_code"], fail_list)
    assert "reason" in checks["missing_icmp_code"]
    assert fail_list[1]["reason"] == checks["missing_icmp_code"]["expected_reason"]

    assert not h.validate_icmp(checks["invalid_icmp_type"], fail_list)
    assert "reason" in checks["invalid_icmp_type"]
    assert fail_list[2]["reason"] == checks["invalid_icmp_type"]["expected_reason"]

    assert not h.validate_icmp(checks["invalid_icmp_code"], fail_list)
    assert "reason" in checks["invalid_icmp_code"]
    assert fail_list[3]["reason"] == checks["invalid_icmp_code"]["expected_reason"]

    assert h.validate_icmp(checks["valid_icmp"], fail_list)
    assert "reason" not in checks["valid_icmp"]
    assert len(fail_list) == 4
