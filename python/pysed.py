"""
  OriginalAuthor: Thurston Stone
  Description: Attempt to implement sed functionality in python
  Usage: pysed -h for help
"""

LOG_MESSAGE_PREFIX = "pysed.py"
cmd_desc="""
   Attempt to implement sed functionality in python
   """
cmd_usage="""
   python %prog  [-v verbose_level] 
   -h for help"""

import sys
import os
from optparse import OptionParser
import logging

#--script specific includes--
import glob
import re


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
    print("ERROR: ",self.error)

def validateArgs():
   """
   Function: validateArgs():
   will validate the command line arguments and options passed.
   it returns opts,args
   """

   parser=OptionParser(usage=cmd_usage,description=cmd_desc)
   #general options
   
   parser.add_option("-v",
                        "--verbose",
                        default = "INFO",
                        help="Level of verbose output to Display to stdout (DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)")


   parser.add_option("-s",
                        "--search",
                        default = None,
                        help="search string")

   parser.add_option("-R",
                        "--RecurseRoot",
                        default = None,
                        help="Root directory to start a recursive search")

   parser.add_option("-r",
                        "--replace",
                        default = None,
                        help="replace string")

   parser.add_option("-i",
                        "--inplace",
                        default = False,
                        action = 'store_true',
                        help="apply replacements directly to the file")

   opts,args=parser.parse_args()
   error=None
   if opts.search is None:
      error = "you must supply a search string using -s"
   if opts.inplace and opts.replace is None:
      error = "you must supply a replacement string using -r in order to use -i/--inplace"

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def applyOnFile(file,searchRE,replace = None,inplace = False):
   fd = open(file)
   lines = fd.read()
   fd.close()

   if replace is not None:
      #rep = Replacement(re.compile("logg(ing).(\w+)"),r"\1-\\1-\2")
      rep = Replacement(searchRE,replace)
      updatedLines = rep.searchRE.sub(rep.replace,lines)
      if inplace:
         fd = open(file,"w")
         fd.write(updatedLines)
         fd.close()
      else:
         print(updatedLines)
   else:
      #this should work like grep
      for i,line in enumerate(lines.split("\n")):
         if searchRE.search(line) is not None:
            print("%s:%d: %s"%(file,i+1,line))

class Replacement(object):
   def __init__(self,searchRE,replaceStr):
      self.searchRE = searchRE
      self.replaceStr = replaceStr

   def replace(self,matchObj):
      #put a slash between every character
      identFunc = lambda *args: args
      outputStr = ''.join([y for x in map(identFunc,len(self.replaceStr)*"\\",self.replaceStr) for y in x if y])

      #generate the new string based on where there are only 3 slashes
      newStr = ""
      slashCount = 0
      for thisChar in outputStr:
         if thisChar == "\\":
            slashCount += 1
         else:
            if slashCount == 3:
               try:
                  newStr += matchObj.group(int(thisChar))
               except ValueError:
                  pass
            else:
               newStr += "\\"*(int(slashCount/2))+thisChar
            slashCount = 0
      return newStr

def pysed(search, replace = None, globs = None, recurseRoot = None,
            inplace = False):
   
   searchRE = re.compile(search)
   if len(globs) == 0:
      globs = ['*']

   filelist = []
   if recurseRoot:
      logging.debug('Finding files under "%s"'%recurseRoot)
      from os import walk
      from os.path import join
      import fnmatch
      for root,dirs,files in walk(recurseRoot):
         for globStr in globs:
            logging.debug('Searching for "%s"'%globStr)
            for filename in fnmatch.filter(files,globStr):
               logging.debug('Found File: %s'%join(root,filename))
               filelist.append(join(root,filename))
   else:
      for globStr in globs:
         filelist.extend(glob.glob(globStr))

   #default output to stdout
   for file in filelist:
      if os.path.isfile(file):
         applyOnFile(file,searchRE,replace,inplace)

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   level=getattr(logging,opts.verbose.upper())
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
					
   return pysed(search = opts.search,
                replace = opts.replace,
                globs = args,
                recurseRoot = opts.RecurseRoot,
                inplace = opts.inplace)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage as e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

