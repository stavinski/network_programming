
from scapy.all import *
from dhcp import DHCPInterface, list_network_interfaces
from argparse import ArgumentParser, RawTextHelpFormatter


def main(iface_name, mac, timeout):
    dhcp = DHCPInterface(iface_name, mac, timeout)

    print "[+] sending discover packet"
    offer = dhcp.send_discover()
    if not offer:
        print "[!] offer packet not received"
        return

    print "[+] offer packet received"
    print "[+] sending request packet"

    ack = dhcp.send_request(ip=offer[BOOTP].yiaddr, server_ip=offer[BOOTP].siaddr, xid=offer[BOOTP].xid)
    if not ack:
        print "[!] ack packet not received"
        return

    print "[+] ack packet received"
    ack.display()


if __name__ == "__main__":

    parser = ArgumentParser(description="DHCP tool", epilog=list_network_interfaces(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('iface', type=str, help='network interface to use')
    parser.add_argument("mac", type=str, help="MAC address of network interface")
    parser.add_argument("-t", "--timeout", help="timeout in seconds to wait for response(s)", type=int, default=5)

    args = parser.parse_args()
    main(args.iface, args.mac, args.timeout)
