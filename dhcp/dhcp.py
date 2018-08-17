
from scapy.all import *

conf.verb = False

# required as response IP will not correlate
conf.checkIPaddr = False

LOCAL_MAC = "98:90:96:C4:14:04"
IFACE = "Intel(R) Ethernet Connection I217-LM"

def discover():
    pkt = Ether(src=LOCAL_MAC, dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0", dst="255.255.255.255")/UDP(sport=68, dport=67)/BOOTP(chaddr=LOCAL_MAC, xid=RandInt())/DHCP(options=[
        ("message-type", "discover"),
        "end"
    ])
    #print pkt.display()
    resp = srp1(pkt, iface=IFACE)
    #print resp.display()
    

def main():
    discover()
    
    
if __name__ == "__main__":
    main()