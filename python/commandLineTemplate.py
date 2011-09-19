"""
  OriginalAuthor: 
  Description: 
  Usage:  
"""

LOG_MESSAGE_PREFIX = "commandLineTemplate.py"
cmd_desc="""
   Enter description here
   """
cmd_usage="""
   python %prog  [-v] 
   -h for help"""

import sys
import os
from optparse import OptionParser
import logging


INVALID_USAGE_RETURN_CODE = 2

try:
   LOG_MESSAGE_PREFIX = os.path.basename(os.path.abspath(__file__))
except:
   pass
   

class InvalidUsage(Exception):
  """ Exception class when the file is used incorrectly on the command line """
  def __init__(self,parser,error):
    self.parser=parser
    self.error=error
  def __str__(self):
    return self.error
  def printError(self):
    self.parser.print_usage()
    print "ERROR: ",self.error

def validateArgs():
   """
   Function: validateArgs():
   will validate the command line arguments and options passed.
   it returns opts,args
   """

   parser=OptionParser(usage=cmd_usage,description=cmd_desc)
   #general options
   
   parser.add_option("-v"
                        ,"--verbose"
                        , default = "NOTSET"
                        , help="Level of verbose output to Display to stdout (DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)")

   opts,args=parser.parse_args()
   error=None

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def commandLineTemplate():
    pass

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   level=logging.NOTSET
   if opts.verbose is not None:
      level=getattr(logging,opts.verbose.upper())
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
					
   return commandLineTemplate()

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

