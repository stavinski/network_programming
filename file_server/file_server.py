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
from contextlib import contextmanager

class FileServer:
  
  def __init__(self, port=9001):
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  

  def _service_client(self, conn, addr):
    print "[+] accepted client connection %s:%d" % (addr[0], addr[1])
    filename = conn.recv(1024)
    print "[+] received filename request: %s" % filename
    if conn.send("FILE_CONTENTS") == 0:
        raise RuntimeError("[!] client connection lost")
    
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    
  def open(self):
    self.sock.bind(("", self.port))
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
    self.host = host
    self.port = port
        

  def _send_get_file(self, filename):
    print "[*] getting file: %s" % filename
    self.sock.send(filename)
  

  def _receive_response(self):
      data = ""
      received = self.sock.recv(4096)
      while received != "": # empty signifies connection has been closed so we're are done
          data += received
          received = self.sock.recv(4096)
      
      self.sock.shutdown(socket.SHUT_RDWR)
      self.sock.close()
              
      print "[+] received bytes: %d" % len(data)
      print data
         
           
  def get_file(self, filename):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((self.host, self.port))
    self._send_get_file(filename)   
    self._receive_response()