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
import hashlib


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
                        , default = "INFO"
                        , help="Level of verbose output to Display to stdout (DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)")

   opts,args=parser.parse_args()
   error=None

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def sha1(paths):
   """
   Recursively calculates a checksum representing the contents of all files
   found with a sequence of file and/or directory paths.
   """
   if not hasattr(paths, '__iter__'):
      raise TypeError('sequence or iterable expected not %r!' % type(paths))

   def update_checksum(checksum, dirname, filenames):
      for filename in sorted(filenames):
         path = os.path.join(dirname, filename)
         if os.path.isfile(path):
            logging.debug("Hashing %s"%path)
            fh = open(path, 'rb')
            while 1:
               buf = fh.read(4096)
               if not buf : break
               checksum.update(buf)
            fh.close()

   chksum = hashlib.sha1()

   for path in sorted([os.path.normpath(f) for f in paths]):
      if os.path.exists(path):
         if os.path.isdir(path):
            os.path.walk(path, update_checksum, chksum)
         elif os.path.isfile(path):
            update_checksum(chksum, dirname(path), basename(path))

   return chksum.hexdigest()

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   level=getattr(logging,opts.verbose.upper())
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
					
   return sha1(args)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

