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


def _general_test(test, func):
    """
    Generalized helper function that takes in a test dictionary with
    test values and the validation function to test. It loops over
    each test vlaue and runs the supplied function using the value
    as input. It tracks successes and failures, testing for
    expecting results.
    """
    fail_list = []
    failures = 0
    for val in test.values():
        # If an "expected_reason" is supplied, we expect failure
        if "expected_reason" in val:
            assert not func(val, fail_list)
            assert "reason" in val
            assert fail_list[-1]["reason"] == val["expected_reason"]
            failures += 1
        # Else, we expect success
        else:
            assert func(val, fail_list)
            assert not "reason" in val

    # Ensure the number of logged failures equals the number of actual failures
    assert len(fail_list) == failures


def test_validate_id(checks):
    """
    Test the "validate_id" function.
    """
    _general_test(checks["id"], h.validate_id)


def test_validate_in_intf(checks):
    """
    Test the "validate_in_intf" function.
    """
    _general_test(checks["in_intf"], h.validate_in_intf)


def test_validate_should(checks):
    """
    Test the "validate_should" function.
    """
    _general_test(checks["should"], h.validate_should)


def test_validate_ip(checks):
    """
    Test the "validate_ip" function.
    """
    _general_test(checks["ip"], h.validate_ip)


def test_validate_proto(checks):
    """
    Test the "validate_proto" function.
    """
    _general_test(checks["proto"], h.validate_proto)


def test_validate_port(checks):
    """
    Test the "validate_port" function.
    """
    _general_test(checks["port"], h.validate_port)


def test_validate_icmp(checks):
    """
    Test the "validate_icmp" function.
    """
    _general_test(checks["icmp"], h.validate_icmp)
