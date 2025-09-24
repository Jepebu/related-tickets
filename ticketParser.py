#!/usr/bin/env python3
import pandas as pd
import os

'''
Fields for project dataset are:
subject
body
answer
type
queue
priority
language
version
tag_1
tag_2
tag_3
tag_4
tag_5
tag_6
tag_7
tag_8
'''

class Parser:
  def __init__(self, data_file, **opts):
    self.__df__ = pd.read_csv(data_file)
    self.__df__['ticket_id'] = 'Ticket_' + (self.__df__.index + 1).astype(str)
    self.__dict__.update(opts)
    self.is_initialized = True


  ### filter() will return a list of all items where attr == val.
  ### If no 'val' is supplied, it will return a dict with one list entry for each of the attributes.
  def filter(self, attr, val=None):
    if type(self.__df__) == None:
      raise AttributeError(f"Dataframe is NoneType.")

    if val:
      attributes = [val]
    else:
      attributes = set(self.__df__[attr])

    result_dict = {}
    for A in attributes:
      result_dict[A] = self.__df__[self.__df__[attr] == A]

    return result_dict

### For testing the ticketParser standalone
if __name__ == "__main__":
  file_name = "/home/jepebu/capstone/data/tickets.csv"
  parser = Parser(file_name)
  print(f"English tickets: {len(parser.filter('language','en'))}")
  print(f"German tickets: {len(parser.filter('language','de'))}")
