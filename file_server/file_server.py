# Objects used for serving and receiving file contents
# MAC 2017-03-22 22:04:20

import socket
from contextlib import contextmanager

class FileServerHeader:
  pass

class FileServer:
  
  def __init__(self, port=9001):
    self.clients = []
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
  def _service_client(self, conn, addr):
    print "[+] accepted client connection"
    self.clients.append((conn,addr))
  
  def open(self):
    self.sock.bind(("127.0.0.1", self.port))
    self.sock.listen(5)
    print "[*] fileserver listening on {}".format(self.port)
    while True:
      conn, addr = self.sock.accept()
      self._service_client(conn, addr)
      
  def close(self):
    print "[*] closing file server connection"  
    self.sock.close()
  
@contextmanager
def open_file_server(port):
  server = FileServer(port)
  
  try:
    server.open()
    yield server
  finally:
    server.close() #always call close
  
class FileClient:
  
  def __init__(self, host="127.0.0.1", port=9001):
    self._connected = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.host = host
    self.port = port
  
  def _get_version(self):
    if not self._connected:
      raise EnvironmentError
    
    self.sock.send("VERSION")
  
  def _get_file(self, filename):
    if not self._connected:
      raise EnvironmentError
    
    self.sock.send("GET:%s" % filename)
  
  def connect(self):
    self.sock.connect((self.host, self.port))
    
  
  def disconnect(self):
    pass