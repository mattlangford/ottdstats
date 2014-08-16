import socket
import sys


class Query:
   'Common base class for all employees'
   empCount = 0

   def __init__(self, server_interface):
      self.interface = server_interface

   def do_query(self):
       pass



