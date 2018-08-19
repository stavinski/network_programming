
import sys

from scapy.all import *
from argparse import ArgumentParser, RawTextHelpFormatter

# turn off scapy verbosity
conf.verb = False

# required as response IP will not correlate
conf.checkIPaddr = False

# responsible for DHCP comms
class DHCPInterface(object):

    # class consts
    DHCP_SPORT = 68
    DHCP_DPORT = 67
    IP_BROADCAST = "255.255.255.255"
    IP_NULL = "0.0.0.0"
    MAC_BROADCAST = "ff:ff:ff:ff:ff:ff"

    def __init__(self, iface_name, mac, timeout):
        self.iface = None
        self.timeout = timeout
        self.mac = mac
        self.mac_raw = mac.replace(':', '').decode('hex')

        for iface in get_windows_if_list():
            if iface_name == iface["name"]:
                self.iface = iface

        if not self.iface:
            raise ArgumentError("could not find iface: %s" % iface_name)

    def craft_udp_packet(self):
        return Ether(src=self.mac, dst=self.MAC_BROADCAST) / IP(src=self.IP_NULL, dst=self.IP_BROADCAST) / UDP(sport=self.DHCP_SPORT, dport=self.DHCP_DPORT)

    def send_discover(self):
        pkt = self.craft_udp_packet() / BOOTP(chaddr=self.mac_raw, xid=RandInt()) / DHCP(options=[
            ("message-type", "discover"),
            "end"
        ])

        return srp1(pkt, timeout=self.timeout, iface=self.iface["name"])

    def send_request(self, **kwargs):

        myip = kwargs["ip"]
        sip = kwargs["server_ip"]
        xid = kwargs["xid"]

        request = self.craft_udp_packet() / BOOTP(chaddr=self.mac_raw, xid=xid) / DHCP(
            options=[
                ("message-type", "request"),
                ("server_id", sip),
                ("requested_addr", myip),
                "end"])

        return srp1(request, timeout=self.timeout, iface=self.iface["name"])

    def discover_rogues(self):
        print "[+] broadcasting discover packet"
        pkt = self.craft_udp_packet() / BOOTP(
            chaddr=self.mac_raw, xid=RandInt()) / DHCP(options=[
                ("message-type", "discover"),
                "end"
            ])

        print "[+] waiting %d seconds for offers" % self.timeout
        ans, unans = srp(pkt, multi=True, timeout=self.timeout, iface=self.iface["name"])
        if len(ans) < 1:
            print "[!] no DHCP offers, check DHCP server!"
        elif len(ans) == 1:
            print "[+} one DHCP offer => %s" % ans[0][1][Ether].src
        else:
            print "[!] multiple DHCP offers:"
            for resp in ans:
                print "[+] " + resp[1][Ether].src


def list_network_interfaces():
    msg = "network interfaces:\n\n"
    for iface in get_windows_if_list():
        msg += "[%s] => %s\n" % (iface["name"], iface["mac"])

    return msg