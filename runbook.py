#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.data import load_yaml
import xmltodict


def run_checks(task):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs, and records the results.
    Returns a list of strings containing each command issued in sequence.
    """
    checks = task.run(task=load_yaml, file=f"host_vars/{task.host.name}.yaml")

    for chk in checks[0].result["checks"]:
        cmd = (
            "packet-tracer input "
            f"{chk['nameif']} {chk['proto']} "
            f"{chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
            "xml"
        )
        task.run(task=netmiko_send_command, command_string=cmd)


def main():
    """
    Execution begins here.
    """

    # Initialize nornir and invoke the grouped task.
    nornir = InitNornir()

    # Use NAPALM logic to invoke the "get_facts" getter
    result = nornir.run(task=run_checks)
    for host, mresult in result.items():
        print(f"Results for {host}")
        # 0 is return value from run_checks
        # 1 is result from load_yaml
        # 2+ are the netmiko command results
        checks = mresult[1].result["checks"]
        for chk, output in zip(checks, mresult[2:]):
            data = xmltodict.parse(f"<root>{output.result}</root>")
            # import json; print(json.dumps(data, indent=2))
            
            src_intf = f"{data['root']['result']['input-interface']}"
            dst_intf = f"{data['root']['result']['output-interface']}"
            print(
                f"{chk['proto']} "
                f"{src_intf}/{chk['src_ip']}/{chk['src_port']}->"
                f"{dst_intf}/{chk['dst_ip']}/{chk['dst_port']}: "
                f"{data['root']['result']['action']}"
            )


if __name__ == "__main__":
    main()
