#!/usr/bin/env python

# MAC 2017-04-16 16:50:25

# a standup SSH tool that will log attempts to login
# and then log subsequent commands passed to it

import six
import sys
import socket
import threading
import paramiko

from binascii import hexlify
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

# logging
paramiko.util.log_to_file("ssh.log")

# use generated rsa key
host_key = paramiko.RSAKey(filename="ssh_key.key")

class SSHServer(paramiko.ServerInterface):
        
  def __init__(self, config={ "attempts": 0, "allow_public_key": True }):
    self._config = config
    self._attempts = config["attempts"]
  
  def check_channel_request(self, kind, chan_id):
    print "[%d] received channel request: %s" % (chan_id, kind)
    if kind == "session":
      return paramiko.OPEN_SUCCEEDED
    
    return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
  
  
  def check_auth_password(self, username, pwd):
    print "[+] received password auth: [%s] => [%s]" % (username, pwd)
    #print "[*] attempts: %d" % self._attempts
    
    if self._attempts == 0:
      return paramiko.AUTH_SUCCESSFUL
    
    self._attempts -= 1
    return paramiko.AUTH_FAILED
  
  
  def check_auth_publickey(self, username, key):
    print "[+] received public key auth: [%s] => [%s]" % (username, u(hexlify(key.get_fingerprint())))
    if self._config["allow_public_key"]:
      return paramiko.AUTH_SUCCESSFUL
    
    return paramiko.AUTH_FAILED
  
  def get_allowed_auths(self, username):
    allowed = ["password"] # awlways allow password
    if self._config["allow_public_key"]:
      allowed.append("publickey")
    
    return ",".join(allowed)
  
  
  def check_channel_env_request(self, chan, name, value):
    print "[%d] received env request: [%s] => [%s]" % (chan.get_id(), name, value) 
    return True
  
  
  def check_channel_exec_request(self, chan, cmd):
    print "[%d] received exec request: [%s]" % (chan.get_id(), cmd)
     
  
  def check_channel_pty_request(self, chan, term, w, h, pw, ph, modes):
    print "[%d] received pty request" % chan.get_id()
    return True
  
  
  def check_port_forward_request(self, addr, port):
    print "[+] received port forward request: %s:%d" % (addr, port)
    return False
  
  
  def check_global_request(self, kind, msg):
    print "[+] recieved global request: [%s] => [%s]" % (kind, msg)
    return False


  def check_channel_shell_request(self, chan):
    print "[%d] shell request" % chan.get_id()
    return True

def setup_server(client, args):
  try:
    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)
    server = SSHServer()
    
    try:
      transport.start_server(server=server)
    except paramiko.SSHException as e:
      sys.exit("[!] SSH negotiation error: %s" % e.message)
      
    chan = transport.accept(20)
    if chan is None:
      sys.exit("[!] no channel")
      
    print "[%d] authenticated" % chan.get_id()
    
    # this all needs tidying up big time!!!
    
    buffer = six.BytesIO()
    cmd = ""
    fileobj = chan.makefile("rw")
    host_name = args.host_name
    chan.send("%s@%s:~$ " % (transport.get_username(), host_name))
    while True:
        byte = fileobj.read(1)
        if not byte or byte == '\x04':
          break
        elif byte == b'\t':
          pass
        elif byte == b'\x7f':
          if buffer.len > 0:
            fileobj.write('\b \b')
            buffer.truncate(buffer.len - 1)
        elif byte in (b'\r', b'\n'):
          print "[%d] received: %s" % (chan.get_id(), buffer.getvalue())
          
          if buffer.getvalue() in ["exit", "logout"]:
            chan.send("\r\nlogout\r\n")
            chan.send_exit_status(1)
            break
          
          fileobj.write("\r\n")
          chan.send("%s@%s:~$ " % (transport.get_username(), host_name))
          buffer = six.BytesIO()
          buffer
        else:
          #logger.debug(repr(byte))
          buffer.write(byte)
          fileobj.write(byte)
                          
  finally:
    chan.shutdown(2)
    chan.close()
    transport.close()

def setup_socket(args):
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    addr = (args.ip_address, args.port)
    sock.bind(addr)
  except socket.error as e:
    sys.exit("[!] could not bind to address: %s" % e.strerror)
    
  try:
    sock.listen(100)
    print "[*] listening on %s:%d" % (args.ip_address, args.port)
    
    while True:
      (client, addr) = sock.accept()
      print "[+] received client connection %s:%d" % (addr[0], addr[1])
      client_handler = threading.Thread(target=setup_server, args=(client, args))
      client_handler.start()
  except socket.error as e:
    sys.exit("[!] could not listen and accept: %s" % e.strerror)
  except KeyboardInterrupt:
    sys.exit("[!] stopping")
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
  
def main():
  parser = ArgumentParser("SSH Logger", formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("ip_address", type=str, help="ip address to bind to", default="")
  parser.add_argument("port", type=int, help="ip address to bind to (best to avoid <= 1024 otherwise root access required)")
  parser.add_argument("--host_name", type=str, help="name of host to use", default="localhost")
  args = parser.parse_args()
  
  setup_socket(args)

if __name__ == "__main__":
  main()
