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
# import json


def run_checks(task):
    """
    Loads in host-specific variables, assembles proper 'packet-tracer'
    commands, issues them to the Cisco ASAs, and records the results.
    Returns a list of strings containing each command issued in sequence.
    """
    checks = task.run(task=load_yaml, file=f"host_vars/{task.host.name}.yaml")

    cmds = []
    for chk in checks[0].result["checks"]:
        cmd = (
            "packet-tracer input "
            f"{chk['nameif']} {chk['proto']} "
            f"{chk['src_ip']} {chk['src_port']} "
            f"{chk['dst_ip']} {chk['dst_port']} "
            "xml"
        )
        cmds.append(cmd)

    for cmd in cmds:
        task.run(task=netmiko_send_command, command_string=cmd)

    return cmds


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
        breakpoint()
        # 0 is return value from run_checks
        # 1 is result from load_yaml
        # 2+ are the netmiko command results
        for cmd, output in zip(mresult[0].result, mresult[2:]):
            xml_text = f"<root>{output.result}</root>"
            data = xmltodict.parse(xml_text)
            # print(json.dumps(data, indent=2))

            print(f"\n- {cmd}")
            failed = False
            for phase in data["root"]["Phase"]:
                print(f"  {phase['id']}/{phase['type']} -> ", end="")
                if phase["result"] == "DROP":
                    print(f"DROP: {data['root']['result']['drop-reason']}")
                    failed = True
            if not failed:
                print("ALLOW")


if __name__ == "__main__":
    main()
