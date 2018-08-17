<<<<<<< HEAD
#!/usr/bin/env python

from argparse import ArgumentParser
from file_server import FileServer, open_file_server

def main():
  parser = ArgumentParser("file server")
  parser.add_argument("-p", "--port", type=int, default=9001, help="port to run on")
  parser.add_argument("-v", "--verbose", type=bool, default=False, help="turn on verbosity logging")
  args = parser.parse_args()
  
  try:
    with open_file_server(args.port) as server:
      print "[*] started file server"
  except KeyboardInterrupt:
    print "[-] stopping file server"

if __name__ == "__main__":
  main()
=======
#!/usr/bin/env python

from argparse import ArgumentParser
from file_server import FileServer, open_file_server

def main():
  parser = ArgumentParser("file server")
  parser.add_argument("-p", "--port", type=int, default=9001, help="port to run on")
  parser.add_argument("-v", "--verbose", default=False, help="turn on verbosity", action="store_true")
  args = parser.parse_args()
    
  try:
    with open_file_server(args.port) as server:
      server.verbose = args.verbose
      print "[*] started file server"
  except KeyboardInterrupt:
    print "[-] stopping file server"

if __name__ == "__main__":
  main()
>>>>>>> c526f9583b889d41c2409e518ea8dede64a5f599
