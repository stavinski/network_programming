import struct
import socket
import os
import sys

from ctypes import *

# map network bytes into useable IP structure
class IPHeader(Structure):
	_fields_ = [
		("ihl_version", c_ubyte),
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
	
	
	def src_ip(self):
		return socket.inet_ntoa(struct.pack("L",self.src_addr))
	
	
	def dst_ip(self):
		return socket.inet_ntoa(struct.pack("L",self.dst_addr))

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
			data = sock.recv(65565)
			header = IPHeader.from_buffer_copy(data)
			src = resolve_ip(header.src_ip())
			dst = resolve_ip(header.dst_ip())
			
			print "src: %s dst: %s len: %d ttl: %d" % (src, dst, header.tot_len, header.ttl)
	except KeyboardInterrupt:
		if is_windows():
			sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
			
		print "[*] closing socket connection"
		
if __name__ == "__main__":
	if len(sys.argv) < 2:
		sys.exit("[!] please enter host ip to listen")
		
	main(sys.argv[1])