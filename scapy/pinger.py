#!/usr/bin/env python

import time
import os
import argparse
import ipaddress
import socket

from errno import EACCES, EPERM
from scapy.all import *

# ICMP types
ICMP_ECHOREPLY = 0
ICMP_DEST_UNREACHABLE = 8

def has_previleges():
    # try and open socket as raw
    try:
        socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except (IOError, OSError) as e:
        if (e.errno == EACCES or e.errno == EPERM):
            print "[-] Error: access denied, try running with root previleges"
            exit(1)
        else:
            raise    

def parse_destination(raw):
    dest = None
    
    try:
        dest = ip_address(raw)
    except:
        try:
            dest = socket.gethostbyname(raw)
            dest = ip_address(dest)
        except:
            pass

    return dest

def ping(dest, seq):
    payload = 'ABCDEFGHIJKLMNOPQRSTUVQXYZ0123456789'
    start = time.clock()
    id = os.getpid()
    ping = IP(dst=dest)/ICMP(id=id, seq=seq)/payload
    resp = sr1(ping,verbose=0, timeout=1)
    duration = (time.clock() - start) * 10
    
    if resp is None:
        print "[-] request timed out"
        return
    
    ip = resp.getlayer(IP)
    icmp = resp.getlayer(ICMP)
    
    if int(icmp.type) == ICMP_ECHOREPLY:
        print "[+] {0} bytes received from {1}: icmp_seq={2} ttl={3}, time={4:.2f}ms".format(ip.len, ip.src, icmp.seq, ip.ttl, duration)        
        return
        
    if int(icmp.type) == ICMP_DEST_UNREACHABLE:
        print "[-] destination unreachable: icmp_code={0}".format(icmp.code)
        return
    
    print "[-] unrecognized icmp type returned: icmp_code={0} icmp_type={1}".format(icmp.code, icmp.type)
    
def main():
    parser = argparse.ArgumentParser('pinger', usage='pinger.py (-d|--destination) [ip or host]')
    parser.add_argument('-d', '--destination',type=str,help='ip or host address to ping')

    has_previleges()
    
    args = parser.parse_args()
    dest = parse_destination(args.destination)
    
    if dest is None:
        print ("[-] Error: invalid host or ip address entered");
        sys.exit(1);
    
    # keep pinging till we get a keyboard interrupt
    while True:
        seq = 1
        
        try:    
            ping(dest, seq)
            time.sleep(1)
            seq += 1                    
        except KeyboardInterrupt:
            break
        
if __name__ == "__main__":
    main()