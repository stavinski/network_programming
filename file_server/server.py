#!/usr/bin/env python

from argparse import ArgumentParser
from file_server import FileServer, open_file_server

def main():
  parser = ArgumentParser("file server")
  parser.add_argument("-p", "--port", type=int, default=9001, help="port to run on")
  parser.add_argument("-v", "--verbose", type=bool, default=false, help="turn on verbosity")
  args = parser.parse_args()
  
  try:
    with open_file_server(args.port) as server:
      print "[*] started file server"
  except KeyboardInterrupt:
    print "[-] stopping file server"

if __name__ == "__main__":
  main()
