import xmltodict
import os
import json
class ProcBase:
    def task_started(self, task):
        pass

    def task_completed(self, task, aresult):
        pass

    def task_instance_started(self, task, host):
        pass

    def task_instance_completed(self, task, host, mresult):
        pass

    def subtask_instance_started(self, task, host):
        pass

    def subtask_instance_completed(self, task, host, mresult):
        pass

class ProcJSON(ProcBase):
    def __init__(self):
        self.data = {}

    def task_completed(self, task, aresult):
        try:
            os.mkdir("outputs") 
        except FileExistsError:
            pass
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
        try:
            os.mkdir("outputs") 
        except FileExistsError:
            pass
        with open("outputs/result.txt", "w") as handle:
            handle.write(self.text)


class ProcCSV(ProcBase):
    def __init__(self):
        self.text = (
            "host,id,proto,icmp type,icmp code,src_ip,src_port,dst_ip,"
            "dst_port,in_intf,out_intf,action,drop_reason,success\n"
        )

    def task_completed(self, task, aresult):
        try:
            os.mkdir("outputs") 
        except FileExistsError:
            pass
        with open("outputs/result.csv", "w") as handle:
            handle.write(self.text)

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
                proto = str(chk["proto"]).lower()
                text = f"{host.name},{chk['id']},{chk['proto']},"

                # Check for TCP or UDP
                if proto in ["tcp", "udp"]:
                    text += (
                        f",,{chk['src_ip']},{chk['src_port']},"
                        f"{chk['dst_ip']},{chk['dst_port']},"
                    )

                # Check for ICMP
                elif proto == "icmp":
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
                self.text += text + "\n"
