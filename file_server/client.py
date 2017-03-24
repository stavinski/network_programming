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
  
  while True:
      choice = raw_input("[*] enter filename or empty for exit: ")
      if choice == "":
          print "[*] exiting"
          sys.exit()
      else:
          client.get_file(choice)


if __name__ == "__main__":
  main()
