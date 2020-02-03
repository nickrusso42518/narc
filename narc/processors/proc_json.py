#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in JSON format.
"""

import json
import xmltodict
from narc.processors.proc_base import ProcBase


class ProcJSON(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the JSON format.
    """

    def __init__(self):
        """
        Constructor initializes an empty dictionary to hold
        the results.
        """
        self.data = {}

    def task_completed(self, task, aresult):
        """
        After the task is completed for all hosts, write the JSON
        data to an output file.
        """
        super().task_completed(task, aresult)
        with open("outputs/result.json", "w") as handle:
            json.dump(self.data, handle, indent=2)

    def task_instance_started(self, task, host):
        """
        When each host begins running the task, create an empty
        dictionary for that host that holds individual results.
        """
        self.data[host.name] = {}

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the JSON dictionaries based on the results, and update
        the main data dictionary for use later.
        """
        checks = mresult[1].result["checks"]
        failonly = task.params["args"].failonly

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):

            # Convert from XML to Python objects, using the check id
            # hostname as the topmost key. Use a dummy key in case the
            # check id has spaces (which should be honored)
            jdata = xmltodict.parse(f"<dummy>{output.result}</dummy>")

            # Replace dummy key with ID (can contain spaces)
            jdata[chk["id"]] = jdata.pop("dummy")
            action = jdata[chk["id"]]["result"]["action"]
            success = chk["should"].lower() == action.lower()
            if (not failonly) or (failonly and not success):
                self.data[host.name].update(jdata)

        # If there are no entries for this host, delete the hostname key
        if len(self.data[host.name]) == 0:
            self.data.pop(host.name)
