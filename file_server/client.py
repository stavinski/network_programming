#!/usr/bin/env python

# MAC 2017-03-22 22:08:47

import sys

from argparse import ArgumentParser
from file_server import FileClient

def main():
  parser = ArgumentParser("File server client")
  parser.add_argument("host", type=str, help="host file server to connect to")
  parser.add_argument("port", type=int, help="port file server to use")
  args = parser.parse_args()

  client = FileClient(args.host, args.port)

  try:
      client.connect()
      print "[*] connecting to %s:%i" % (args.host, args.port)
  except:
      sys.exit("[!] could not connect to host")
  finally:      
      client.disconnect()
      
if __name__ == "__main__":
  main()
