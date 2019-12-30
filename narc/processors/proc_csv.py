#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in CSV format.
"""

import xmltodict
from narc.processors.proc_base import ProcBase


class ProcCSV(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the CSV format.
    """

    def __init__(self):
        """
        Constructor defines a string containing column headers
        to hold the results.
        """
        self.text = (
            "host,id,proto,icmp type,icmp code,src_ip,src_port,dst_ip,"
            "dst_port,in_intf,out_intf,action,drop_reason,success\n"
        )

    def task_completed(self, task, aresult):
        """
        After the task is completed for all hosts, write the CSV
        data to an output file.
        """
        super().task_completed(task, aresult)
        with open("outputs/result.csv", "w") as handle:
            handle.write(self.text)

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the CSV rows based on the results, and append them to
        the text string for use later.
        """
        checks = mresult[1].result["checks"]
        failonly = task.params["args"].failonly

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
                self.text += f"{host.name},{chk['id']},{chk['proto']},"

                # Check for TCP or UDP
                if proto in ["tcp", "udp"]:
                    self.text += (
                        f",,{chk['src_ip']},{chk['src_port']},"
                        f"{chk['dst_ip']},{chk['dst_port']},"
                    )

                # Check for ICMP
                elif proto == "icmp":
                    self.text += (
                        f"{chk['icmp_type']},{chk['icmp_code']},"
                        f"{chk['src_ip']},,{chk['dst_ip']},,"
                    )

                # Protocol is an uncommon protocol specified numerically
                else:
                    self.text += f",,{chk['src_ip']},,{chk['dst_ip']},,"

                # Finish the text by adding the drop reason (optional)
                # and ingress/egress interfaces, which are protocol-agnostic
                in_intf = data["root"]["result"].get("input-interface", "")
                out_intf = data["root"]["result"].get("output-interface", "")
                reason = data["root"]["result"].get("drop-reason", "")
                self.text += f"{in_intf},{out_intf},{action},{reason},{success}\n"
