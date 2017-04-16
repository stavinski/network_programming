# Objects used for serving and receiving file contents
# MAC 2017-03-22 22:04:20

"""
FileServer will receieve a specific operation from a client
will return the response and end the connection similar
process to HTTP this enables the client to know when the
conversation is over by receiving 0 bytes in the receive
and keeps it simpler
"""

import socket

from os import path
from contextlib import contextmanager

# defaults
default_host = "127.0.0.1"
default_port = 9001

class Logging:
  
  def __init__(self):
    self._verbose = False
      
  @property
  def verbose(self):
    return self._verbose
  

  @verbose.setter
  def verbose(self, value):
    self._verbose = bool(value)
  
  
  def log_standard(self, message):
    print message
  
  
  def log_verbose(self, message):
    if self._verbose:
      print message
  

class FileServer(Logging):
  
  def __init__(self, port=default_port):
    Logging.__init__(self)
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
      
  def _service_client(self, conn, addr):
    root_path = path.join(path.curdir, "files")
    Logging.log_verbose(self, "[+] accepted client connection %s:%d" % (addr[0], addr[1]))
    filename = conn.recv(1024)
    Logging.log_verbose(self, "[+] received filename request: %s" % filename)
    
    try:
      with open(path.join(root_path, filename), "rb", buffering=4096) as file:
        data = file.read()
        while len(data) > 0:
          if conn.send(data) == 0:
            Logging.log_standard(self, "[!] client connection lost")
            break
        
          data = file.read() # get the next data
    except IOError as e:
      Logging.log_standard(self, "[!] error while reading file: %s" % str(e))
      conn.send("ERR: could not read file %s" % filename)
    finally:
      Logging.log_verbose(self, "[*] shutting down connection to client")
      conn.shutdown(socket.SHUT_RDWR)
      conn.close()
      
  def open(self):
    self.sock.bind(("", self.port))
    self.sock.listen(1)
    Logging.log_standard(self, "[*] fileserver listening on: {}".format(self.port))
    while True:
      conn, addr = self.sock.accept()
      self._service_client(conn, addr)
    
        
  def close(self):
    Logging.log_standard(self, "[*] closing file server connection")
    self.sock.shutdown(socket.SHUT_RDWR)
    self.sock.close()
  
@contextmanager
def open_file_server(port):
  server = FileServer(port)
  
  try:
    server.open()
    yield server
  finally:
    server.close() #always call close
  

class FileClient(Logging):
    
  def __init__(self, host=default_host, port=default_port):
    Logging.__init__(self)
    self.host = host
    self.port = port
        

  def _send_get_file(self, filename):
    Logging.log_standard(self, "[*] getting file: %s" % filename)
    self.sock.send(filename)
  

  def _receive_response(self):
      data = ""
      received = self.sock.recv(4096)
      while received != "": # empty signifies connection has been closed so we're are done
          if received.startswith("ERR:"):
            Logging.log_standard(self, "[!] %s" % received)
            break
          
          data += received
          received = self.sock.recv(4096)
      
      self.sock.shutdown(socket.SHUT_RDWR)
      self.sock.close()
              
      Logging.log_verbose(self, "[+] received bytes: %d" % len(data))
      Logging.log_standard(self, data)
         
           
  def get_file(self, filename):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
    self.sock.connect((self.host, self.port))
    self._send_get_file(filename)   
    self._receive_response()