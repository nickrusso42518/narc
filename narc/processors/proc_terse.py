import xmltodict
from narc.processors.proc_base import ProcBase

class ProcTerse(ProcBase):
    def __init__(self):
        self.text = ""

    def task_instance_completed(self, task, host, mresult):
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
                print(output)

    def task_completed(self, task, aresult):
        super().task_completed(task, aresult)
        with open("outputs/result.txt", "w") as handle:
            handle.write(self.text)
