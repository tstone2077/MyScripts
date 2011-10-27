#!/usr/bin/python
"""
  OriginalAuthor: Thurston Stone
  Description: Move files older than a given age into a separate directory
  Usage: archive.py --help 
"""

LOG_MESSAGE_PREFIX = "archive.py"
cmd_desc="""
   Move files older than a given age into a separate directory
   """
cmd_usage="""
   python %prog  [-v] [-a <int>] [-x <exclude_dirs>] rootDir archiveDir
   -h for help"""

import sys
import os
from optparse import OptionParser
import logging
import datetime
import time
import shutil

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

   parser.add_option("-a"
                        , "--age"
                        , type="int"
                        , default = 30
                        , help="Any files older than this amount of days will be moved")

   parser.add_option("-x"
                        , "--exclude-text"
                        , default = None
                        , dest = "excludeText"
                        , help="comma separated list of text whic if found in any of the root files, will not be moved")

   parser.add_option(""
                        , "--dry-run"
                        , dest = "dryRun"
                        , action="store_true"
                        , default = False
                        , help="print out what would happen, but do not write anything to the disk")
   opts,args=parser.parse_args()
   error=None
   if len(args) != 2:
     error = "Must supply the root directory and the destination directory"

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def archive(age,rootDir,archiveDir,excludeText = None,dryRun = False):

   if dryRun:
     logging.info("***Dry run: No files will be written to the disk***")
   if excludeText is None:
      excludeText = [""] #match everything
   baseDate = datetime.date.today() - datetime.timedelta(days=age)
   #get a list of all the files
   oldFiles = []
   for root,dirs,files in os.walk(rootDir):
      for file in files:
         fullFilePath = os.path.join(root,file)
         year,month,day = time.localtime(os.stat(fullFilePath).st_mtime)[:3]
         lastUsed = datetime.date(year,month,day)
         if lastUsed < baseDate:
            for exText in excludeText:
               if not fullFilePath.find(exText) > 0:
                  oldFiles.append(fullFilePath)

   logging.info("Backing up %d file(s)"%len(oldFiles))
   filesMoved=0
   for file in oldFiles:
      src = file
      #dst = file.replace(rootDir,archiveDir)
      relativeFileName = file[len(rootDir):]
      if len(relativeFileName) != len(file) and relativeFileName[0] == '/':
         relativeFileName = relativeFileName[1:]
      dst = os.path.join(archiveDir,relativeFileName)
      dstDir = os.path.dirname(dst)
      if not os.path.exists(dstDir):
         logging.info("Making Directory %s"%dstDir)
         if not dryRun:
            os.makedirs(dstDir)
      logging.info("Archiving: %s"%src)
      logging.debug("To: %s"%dst)
      if not dryRun:
         shutil.move(src,dst)
         filesMoved=filesMoved+1
   logging.info("Moved %d file(s)"%filesMoved)

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   excludeText=None
   if opts.excludeText is not None:
      excludeText=opts.excludeText.split(",")
   level=logging.NOTSET
   if opts.verbose is not None:
      level=getattr(logging,opts.verbose.upper())
   if opts.dryRun:
      level=logging.INFO
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
   return archive(opts.age,args[0],args[1],excludeText,opts.dryRun)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

