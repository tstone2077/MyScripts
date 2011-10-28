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
from progressbar import ProgressBar, Counter, Timer, Percentage, Bar, FormatLabel


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

class HashPath:
   def __init__(self,path,showProgress=False):
      if not os.path.exists(path):
         raise OSError("File Not Found")
      self.root = path
      self.checksum = hashlib.sha1()
      self.path = os.path.abspath(path)
      #get a directory/file listing for this path as well as the total size
      (self.listing,self.size) = self.__scan_path(showProgress)
   def __str__(self):
      return "Size=%d,ListingLength=%d,Path=%s"%(self.size,len(self.listing),self.path)
   def __scan_path(self,showProgress):
      logging.debug("Scanning for files and sizes of %s"%self.path)
      size = 0
      listing = []
      if os.path.isdir(self.path):
         if showProgress:
            pbar = ProgressBar(1,[self.path," : ", Counter()," Files scanned. ", Timer()])
            pbar.start()
         for root,dirs,files in os.walk(self.path):
            if len(files) == 0:
               listing.append(root)
            else:
               for file in files:
                  filename = os.path.join(root,file)
                  size += os.path.getsize(filename)
                  listing.append(filename)
                  length = len(listing)
                  if showProgress:
                     pbar.maxval = length
                     if length%25==0:
                        pbar.update(length)
         if showProgress:
            pbar.finish()
      else:
         listing.append(os.path.basename(self.path))
         size+=os.path.getsize(self.path)
      listing.sort()
      return (listing,size)
   def calculateHash(self,pbar=None):
      for file in self.listing:
         if os.path.isfile(file):
            #we only want to operate on files
            logging.debug("Hashing file: %s"%file)
            fh = open(file)
            if pbar is not None:
               startPos = pbar.currval
            while 1:
               buf = fh.read(4096)
               if not buf : break
               self.checksum.update(buf)
               if pbar is not None:
                  #raw_input("%s: %d/%d = %d"%(file,startPos+fh.tell(),pbar.maxval,(startPos+fh.tell())/pbar.maxval*100))
                  pbar.update(startPos+fh.tell())
            fh.close()
      return self.checksum.hexdigest()

def GetHumanReadable(size,precision=2):
   suffixes=['B','KB','MB','GB','TB']
   suffixIndex = 0
   while size > 1024:
      suffixIndex += 1 #increment the suffix
      size = size/1024.0 #apply the division
   return "%.*f%s"%(precision,size,suffixes[suffixIndex])


def sha1(paths,showProgress=False):
   hashPaths = []
   hashes = []
   totalSize = 0
   for path in paths:
      hashPath = HashPath(path,showProgress)
      hashPaths.append(hashPath)
      totalSize += hashPath.size

   logging.info("Hashing %s"%GetHumanReadable(totalSize))
   pbar=None
   if showProgress:
      pbar = ProgressBar(totalSize,[FormatLabel('Processed %(value)d B in %(elapsed)s'),Bar()])
      pbar.start()
   for hashPath in hashPaths:
      hashes.append(hashPath.calculateHash(pbar))
      logging.info(hashPath.checksum.hexdigest())
   if showProgress:
      pbar.finish()

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   level=getattr(logging,opts.verbose.upper())
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
					
   return sha1(args,True)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

