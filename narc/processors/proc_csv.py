import xmltodict
from narc.processors.proc_base import ProcBase

class ProcCSV(ProcBase):
    def __init__(self):
        self.text = (
            "host,id,proto,icmp type,icmp code,src_ip,src_port,dst_ip,"
            "dst_port,in_intf,out_intf,action,drop_reason,success\n"
        )

    def task_completed(self, task, aresult):
        super().task_completed(task, aresult)
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
