#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in a terse, text-based format.
"""

import xmltodict
from narc.processors.proc_base import ProcBase


class ProcTerse(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the terse, text-based format.
    """

    def __init__(self):
        """
        Constructor initializes an empty string to hold
        the results.
        """
        self.text = ""

    def task_completed(self, task, aresult):
        """
        After the task is completed for all hosts, write the text
        data to an output file.
        """
        super().task_completed(task, aresult)
        with open("outputs/result.txt", "w") as handle:
            handle.write(self.text)

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the text output based on the results, and append them to
        the text string for use later.
        """
        if isinstance(mresult[1].result, str):
            breakpoint()
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
                status = "PASS" if success else "FAIL"
                output = f"{host.name[:12]:<12} {chk['id'][:24]:<24} -> {status}"
                self.text += output + "\n"
