#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

import json
import xmltodict


def _style_json(aresult, failonly):
    """
    Prints the result in JSON format which includes the user-specified
    name and overall test result.
    """
    root_dict = {}
    overall_success = True
    for host, mresult in aresult.items():
        checks = mresult[1].result["checks"]
        host_dict = {}

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):

            # Convert from XML to Python objects, using the check id
            # hostname as the topmost key. Use a dummy key in case the
            # check id has spaces (which should be honored)
            # chk_id = chk["id"].replace(" ", "_")
            data = xmltodict.parse(f"<dummy>{output.result}</dummy>")

            # Replace dummy key with ID (can contain spaces)
            data[chk["id"]] = data.pop("dummy")
            action = data[chk["id"]]["result"]["action"]
            success = chk["should"].lower() == action.lower()
            if (not failonly) or (failonly and not success):
                host_dict.update(data)
            if not success:
                overall_success = False

            # Only add a host-specific dict if it contains something
            if len(host_dict) > 0:
                root_dict.update({host: host_dict})

    print(json.dumps(root_dict, indent=2))
    return overall_success


def _style_csv(aresult, failonly):
    """
    Prints the result in CSV format which includes the user-specified
    id and overall test result. The columns are as follows, split into
    two lines for readability.
        host,id,proto,icmp type, icmp code,src_ip,src_port,dst_ip,
        dst_port,in_intf,out_intf,action,drop_reason,success
    """
    print(
        "host,id,proto,icmp type,icmp code,src_ip,src_port,dst_ip,"
        "dst_port,in_intf,out_intf,action,drop_reason,success"
    )
    overall_success = True
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
                proto = str(chk["proto"]).lower()
                text = f"{host},{chk['id']},{chk['proto']},"

                # Check for TCP (6) or UDP (17)
                if proto in ["tcp", "6", "udp", "17"]:
                    text += (
                        f",,{chk['src_ip']},{chk['src_port']},"
                        f"{chk['dst_ip']},{chk['dst_port']},"
                    )

                # Check for ICMP (1)
                elif proto in ["icmp", "1"]:
                    text += (
                        f"{chk['icmp_type']},{chk['icmp_code']},"
                        f"{chk['src_ip']},,{chk['dst_ip']},,"
                    )

                # Protocol is an uncommon protocol specified numerically
                else:
                    text += f",,{chk['src_ip']},,{chk['dst_ip']},,"

                # Finish the text by adding the drop reason (optional)
                # and ingress/egress interfaces, which are protocol-agnostic
                in_intf = f"{data['root']['result']['input-interface']}"
                out_intf = f"{data['root']['result']['output-interface']}"
                drop_reason = data["root"]["result"].get("drop-reason", "")
                text += f"{in_intf},{out_intf},{action},{drop_reason},{success}"
                print(text)

            if not success:
                overall_success = False

    return overall_success


def _style_terse(aresult, failonly):
    """
    Prints the result in terse format (compressed to one line)
    Example output is shown below:
     ASAV1: DNS OUTBOUND success -> True
     ASAV1: HTTPS OUTBOUND success -> False
    """
    overall_success = True
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
                passfail = "PASS" if success else "FAIL"
                print(f"{host[:12]:<12} {chk['id'][:24]:<24} -> {passfail}")

            if not success:
                overall_success = False

    return overall_success


def process_result(aresult, failonly, style="terse"):
    """
    This function serves as an decision point as it calls other functions
    based on the desired "style". The default style is "terse", and if
    an invalid style is supplied, terse is also chosen. The function
    returns True if all checks pass, or False if at least one fails.
    """
    # Evaluate args.style to select a styling function (default is terse)
    style_map = {
        "terse": _style_terse,
        "csv": _style_csv,
        "json": _style_json,
    }
    choice = style_map[style]
    return choice(aresult, failonly)
