
from scapy.all import *

conf.checkIPaddr=False

LOCAL_MAC = "98:90:96:C4:14:04"

def main():
    pkt = Ether(src=LOCAL_MAC, dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0", dst="255.255.255.255")/UDP(sport=68, dport=67)/BOOTP(chaddr=LOCAL_MAC, xid=RandInt())/DHCP(options=[
        ("message-type", "discover"),
        "end"
    ])
    print pkt.display()
    resp = srp1(pkt, iface="Intel(R) Ethernet Connection I217-LM")
    print resp.display()
    
if __name__ == "__main__":
    main()
