import struct
import socket
import os
import sys

from ctypes import *

# map network bytes into useable IP structure
class IPHeader(Structure):
	_fields_ = [
		("ihl", c_ubyte, 4),
		("version", c_ubyte, 4),
		("tos", c_ubyte),
		("tot_len", c_ushort),
		("id", c_ushort),
		("frag_off", c_ushort),
		("ttl", c_ubyte),
		("protocol", c_ubyte),
		("check", c_ushort),
		("src_addr", c_uint),
		("dst_addr", c_uint)
	]
	
	def __new__(self, buffer=None):
		return self.from_buffer_copy(buffer)
		
	def __init__(self, buffer=None):
		self.src_ip = socket.inet_ntoa(struct.pack("<L",self.src_addr))
		self.dst_ip = socket.inet_ntoa(struct.pack("<L",self.dst_addr))

# map network bytes into useable ICMP structure
class ICMPHeader(Structure):
	_fields_ = [
		("type", c_ubyte),
		("code", c_ubyte),
		("checksum", c_ushort),
		("unused", c_ushort),
		("next_hop_mtu", c_ushort)
	]
	
	def __new__(self, buffer=None):
		return self.from_buffer_copy(buffer)
		
	def __init(self, buffer=None):
		pass
		
resolves = {} # hold previous resolves
		
def is_windows():
	return os.name == "nt"

def resolve_ip(ip):
	if not resolves.has_key(ip):
		try:
			resolves[ip] = socket.gethostbyaddr(ip)[0]
		except:
			resolves[ip] = ip # if we can't resolve just use the ip
	
	return resolves[ip]
	
def main(host):
	
	if is_windows():
		socket_proto = socket.IPPROTO_IP
	else:
		socket_proto = socket.IPPROTO_ICMP
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_proto)
	sock.bind((host, 0))
	
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	
	if is_windows():
		sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
				
	print "[*] listening on socket"
	
	try:
		while True:
			data = sock.recvfrom(65565)[0]
			ip_header = IPHeader(data[0:20])
			src = resolve_ip(ip_header.src_ip)
			dst = resolve_ip(ip_header.dst_ip)
			
			print "[+] proto: %x \t %s -> %s" % (ip_header.protocol, src, dst)
			
			if ip_header.protocol == socket.IPPROTO_ICMP:
				offset = ip_header.ihl * 4 # length is in words (32 bits)
				buf = data[offset:offset + sizeof(ICMPHeader)]
				
				icmp_header = ICMPHeader(buf)
				
				print "[+] received ICMP type=%d code=%d" % (icmp_header.type, icmp_header.code)
			
	except KeyboardInterrupt:
		if is_windows():
			sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
			
		print "[*] closing socket connection"
		
if __name__ == "__main__":
	if len(sys.argv) < 2:
		sys.exit("[!] please enter host ip to listen")
		
	main(sys.argv[1])