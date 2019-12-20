#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import json
import xmltodict


def style_json(aresult, failonly):
    """
    Prints the result in JSON format which includes the user-specified
    name and overall test result.
    """
    root_dict = {}
    for host, mresult in aresult.items():
        checks = mresult[1].result["checks"]
        host_dict = {}

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):

            # Convert from XML to Python objects, using the check name
            # hostname as the topmost key. Spaces in the check names are
            # replaced with underscopes to form proper XML
            chk_name = chk["name"].replace(" ", "_")
            data = xmltodict.parse(f"<{chk_name}>{output.result}</{chk_name}>")
            action = data[chk_name]["result"]["action"]
            success = chk["should"].lower() == action.lower()
            if (not failonly) or (failonly and not success):
                host_dict.update(data)

        root_dict.update({host: host_dict})

    print(json.dumps(root_dict, indent=2))


def style_csv(aresult, failonly):
    """
    Prints the result in CSV format which includes the user-specified
    name and overall test result. The columns are as follows, split into
    two lines for readability.
        name,proto,src_ip,src_port,dst_ip,dst_port,
        in_intf,out_intf,action,drop_reason,success
    """
    print(
        "host,name,proto,src_ip,src_port,dst_ip,dst_port,"
        "in_intf,out_intf,action,drop_reason,success"
    )
    for host, mresult in aresult.items():
        checks = mresult[1].result["checks"]

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):
            # Convert from XML to Python objects, using the device
            # hostname as the topmost key
            data = xmltodict.parse(f"<root>{output.result}</root>")
            action = data["root"]["result"]["action"]
            success = chk["should"].lower() == action.lower()

            if (not failonly) or (failonly and not success):
                drop_reason = data["root"]["result"].get("drop-reason", "")
                in_intf = f"{data['root']['result']['input-interface']}"
                out_intf = f"{data['root']['result']['output-interface']}"
                print(
                    f"{host},{chk['name']},{chk['proto']},"
                    f"{chk['src_ip']},{chk['src_port']},"
                    f"{chk['dst_ip']},{chk['dst_port']},"
                    f"{in_intf},{out_intf},{action},"
                    f"{drop_reason},{success}"
                )


def style_terse(aresult, failonly):
    """
    Prints the result in terse format (compressed to one line)
    Example output is shown below:
      Results for ASAV1:
       - udp s=192.0.2.1/5000 d=8.8.8.8/53 UNKNOWN->UNKNOWN: drop
       - tcp s=192.0.2.1/5000 d=20.0.0.1/443 UNKNOWN->UNKNOWN: drop
       + tcp s=20.0.0.1/5000 d=192.0.2.1/22 UNKNOWN->UNKNOWN: drop
    """
    for host, mresult in aresult.items():
        print(f"Results for {host}:")
        checks = mresult[1].result["checks"]

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):
            # Convert from XML to Python objects, using the device
            # hostname as the topmost key
            data = xmltodict.parse(f"<root>{output.result}</root>")
            action = data["root"]["result"]["action"]
            success = chk["should"].lower() == action.lower()

            if (not failonly) or (failonly and not success):
                # Print the output using the user-specified style
                in_intf = f"{data['root']['result']['input-interface']}"
                out_intf = f"{data['root']['result']['output-interface']}"
                print(
                    f" {'+' if success else '-'} {chk['proto']} "
                    f"s={chk['src_ip']}/{chk['src_port']} "
                    f"d={chk['dst_ip']}/{chk['dst_port']} "
                    f"{in_intf}->{out_intf}: {action}"
                )
