import json
import xmltodict
from narc.processors.proc_base import ProcBase

class ProcJSON(ProcBase):
    def __init__(self):
        self.data = {}

    def task_completed(self, task, aresult):
        super().task_completed(task, aresult)
        with open("outputs/result.json", "w") as handle:
            json.dump(self.data, handle, indent=2)

    def task_instance_started(self, task, host):
        self.data[host.name] = {}

    def task_instance_completed(self, task, host, mresult):
        checks = mresult[1].result["checks"]
        failonly = task.params["args"].failonly

        # Iterate over the list of checks (input) and the corresponding
        # netmiko results (output)
        for chk, output in zip(checks, mresult[2:]):

            # Convert from XML to Python objects, using the check id
            # hostname as the topmost key. Use a dummy key in case the
            # check id has spaces (which should be honored)
            # chk_id = chk["id"].replace(" ", "_")
            jdata = xmltodict.parse(f"<dummy>{output.result}</dummy>")

            # Replace dummy key with ID (can contain spaces)
            jdata[chk["id"]] = jdata.pop("dummy")
            action = jdata[chk["id"]]["result"]["action"]
            success = chk["should"].lower() == action.lower()
            if (not failonly) or (failonly and not success):
                self.data[host.name].update(jdata)
