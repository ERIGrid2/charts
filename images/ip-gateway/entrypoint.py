
import subprocess
import os
import json
import shlex

class Network:

    def __init__(self, **args):
        for key, val in args.items:
            setattr(self, key, val)

        self.ip = self.ips[0]

    @classmethod
    def load(cls):
        """ Loads multus network status annotation
        
        NETWORK_STATUS = [
            {
                "name": "cbr0",
                "interface": "eth0",
                "ips": [
                    "10.42.2.36"
                ],
                "mac": "02:67:84:3a:47:8e",
                "default": True,
                "dns": {}
            },
            {
                "name": "kube-system/local-bridge",
                "interface": "net1",
                "ips": [
                    "172.23.157.190"
                ],
                "mac": "e2:39:e4:f3:f0:d7",
                "dns": {}
            }
        ]
        
        """

        nets = json.loads(os.environ.get('NETWORK_STATUS', []))

        return [cls(net) for net in nets]

def tc(**args):
    return subprocess.check_call(['tc'] + args)

networks = Network.load()
internal = networks[0]
external = networks[1]

# Internal -> External
## DNAT
tc('qdisc', 'add', 'dev', internal.interface, 'ingress', 'handle', 'ffff')
tc('filter', 'add', 'dev', internal.interface, 'parent', 'ffff:', 'protocol', 'ip', 'prio', '10', 'u32', 'match', 'ip', 'dst', f'{internal.ip}/32', 'action', 'nat', 'ingress', 'f{internal.ip}/32', external.ip)

## SNAT
tc('qdisc', 'add', 'dev', internal.interface, 'root', 'handle', '10:', 'htb') 
tc('filter', 'add', 'dev', internal.interface, 'parent', '10:', 'protocol', 'ip', 'prio', '10', 'u32', 'match', 'ip', 'src', f'{external.ip}/32', 'action', 'nat', 'egress', 'f{external.ip}/32', internal.ip)

# External -> Internal
## DNAT
tc('qdisc', 'add', 'dev', external.interface, 'ingress', 'handle', 'ffff')
tc('filter', 'add', 'dev', external.interface, 'parent', 'ffff:', 'protocol', 'ip', 'prio', '10', 'u32', 'match', 'ip', 'dst', f'{external.ip}/32', 'action', 'nat', 'ingress', f'{external.ip}/32', internal.ip)

## SNAT
tc('qdisc', 'add', 'dev', external.interface, 'root', 'handle 10: htb')
tc('filter', 'add', 'dev', external.interface, 'parent', '10:', 'protocol', 'ip', 'prio', '10', 'u32', 'match', 'ip', 'src', f'{external.ip}/32', 'action', 'nat', 'egress', f'{external.ip}/32', internal.ip)
