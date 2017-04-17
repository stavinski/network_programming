#!/usr/bin/env python

# MAC 2017-04-16 16:50:25

# a standup SSH tool that will log attempts to login
# and then log subsequent commands passed to it

import logging
import six
import sys
import socket
import threading
import paramiko

from binascii import hexlify
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

# logging
paramiko_logger = logging.getLogger("paramiko")
paramiko_logger.setLevel(logging.ERROR)
paramiko_logger.addHandler(logging.StreamHandler())

logger = logging.getLogger("ssh")

# keep record of attempts by ip
attempts = {}


# use generated rsa key
host_key = paramiko.RSAKey(filename="ssh_key.key")

class SSHServer(paramiko.ServerInterface):
        
  def __init__(self, client_ip, config):
    self._client_ip = client_ip
    self._attempts = config.login_attempts
    self._allow_public_key = config.allow_public_key
  
  def check_channel_request(self, kind, chan_id):
    logger.info("[%s] received channel request: %s", self._client_ip, kind)
    if kind == "session":
      return paramiko.OPEN_SUCCEEDED
    
    return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
  
  
  def check_auth_password(self, username, pwd):
    logger.info("[%s] received password auth: [%s] => [%s]", self._client_ip, username, pwd)
    
    if not attempts.has_key(self._client_ip):
      attempts[self._client_ip] = self._attempts
    
    if attempts[self._client_ip] == 0:
      return paramiko.AUTH_SUCCESSFUL
    
    attempts[self._client_ip] -= 1
    return paramiko.AUTH_FAILED
  
  
  def check_auth_publickey(self, username, key):
    logger.info("[%s] received public key auth: [%s] => [%s]", self._client_ip, username, hexlify(key.get_fingerprint()))
    if self._allow_public_key:
      return paramiko.AUTH_SUCCESSFUL
    
    return paramiko.AUTH_FAILED
  
  def get_allowed_auths(self, username):
    allowed = ["password"] # awlways allow password
    if self._allow_public_key:
      allowed.append("publickey")
    
    return ",".join(allowed)
  
  
  def check_channel_env_request(self, chan, name, value):
    logger.info("[%s] received env request: [%s] => [%s]", self._client_ip, name, value) 
    return True
  
  
  def check_channel_exec_request(self, chan, cmd):
    logger.info("[%s] received exec request: [%s]", self._client_ip, cmd)
    return False 
  
  def check_channel_pty_request(self, chan, term, w, h, pw, ph, modes):
    logger.info("[%s] received pty request", self._client_ip)
    return True
  
  
  def check_port_forward_request(self, addr, port):
    logger.info("[%s] received port forward request: %s:%d", self._client_ip, addr, port)
    return False
  
  
  def check_global_request(self, kind, msg):
    logger.info("[%s] received global request: [%s] => [%s]", self._client_ip, kind, msg)
    return False


  def check_channel_shell_request(self, chan):
    logger.info("[%s] shell request", self._client_ip)
    return True

def setup_server(client, client_ip, client_port, args):
  try:
    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)
    server = SSHServer(client_ip, args)
    
    try:
      transport.start_server(server=server)
    except paramiko.SSHException as e:
      sys.exit("[!] SSH negotiation error: %s" % e.message)
      
    chan = transport.accept(20)
    if chan is None:
      sys.exit("[!] no channel")
      
    logger.info("[%s] authenticated", client_ip)
    
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
          logger.info("[%s] received: %s", client_ip, buffer.getvalue())
          
          if buffer.getvalue() in ["exit", "logout"]:
            chan.send("\r\nlogout\r\n")
            chan.send_exit_status(1)
            break
          
          fileobj.write("\r\n")
          chan.send("%s@%s:~$ " % (transport.get_username(), host_name))
          buffer = six.BytesIO()
        else:
          buffer.write(byte)
          fileobj.write(byte)
                          
  finally:      
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
    logger.info("listening on %s:%d", args.ip_address, args.port)
    
    while True:
      (client, addr) = sock.accept()
      logger.info("[%s] client connection", addr[0])
      client_handler = threading.Thread(target=setup_server, args=(client, addr[0], addr[1], args))
      client_handler.start()
  except socket.error as e:
    sys.exit("[!] could not listen and accept: %s" % e.strerror)
  except KeyboardInterrupt:
    sys.exit("[!] stopping")
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def setup_logging(args):
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  
  if args.log_console:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
  if args.log_file is not None:
    file_handler = logging.FileHandler(filename=args.log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main():
  parser = ArgumentParser("SSH Logger", formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("ip_address", type=str, help="ip address to bind to", default="")
  parser.add_argument("port", type=int, help="ip address to bind to (best to avoid <= 1024 otherwise root access required)")
  parser.add_argument("--host-name", type=str, help="name of host to use", default="localhost")
  parser.add_argument("--log-console", help="log output to console", action='store_true', default=False)
  parser.add_argument("--log-file", metavar="LOG_FILE", help="log output to specified file", type=str, default=None)  
  parser.add_argument("--login-attempts", help="number attempts before allowing login", type=int, default=10)
  parser.add_argument("--allow-public-key", help="allow public key login", action="store_true")  
  
  args = parser.parse_args()
  
  setup_logging(args)
  setup_socket(args)

if __name__ == "__main__":
  main()
