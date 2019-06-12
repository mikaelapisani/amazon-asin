#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 23:51:54 2019

@author: mikaelapisanileal
"""
import sys
import getopt
from processor import Processor
from config import Config

def execute_processor(config_path):
    config = Config(config_path)
    processor = Processor(config)
    processor.process_data()
   
def info():
    print('python -c config.properties')        

def main(argv):
    config_path = ''
    try:
        opts, args = getopt.getopt(argv,'hc:',['config='])
    except getopt.GetoptError:
        info()
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         info()
         sys.exit()
      elif opt in ('-c', '--config'):
         config_path = arg

    execute_processor(config_path)
   
if __name__ == "__main__":
    main(sys.argv[1:])




