#!/usr/bin/python
"""
  OriginalAuthor: Thurston Stone
  Description: use truecrypt to encrypt a directory
  Usage: python tc-encrypt-dir.py -h 

NOTE: user must have the privileges to mount a volume

NOTE: we call truecrypt using subprocess.call and shell=True.
This is not a secure thing to do.  
See http://docs.python.org/library/subprocess.html for details.

NOTE: We make a temp directory (logged at the debug level). If there is a traceback error, that directory might not get cleaned up.
"""

LOG_MESSAGE_PREFIX = "tc-encrypt-dir.py"
description="""
   Use truecrypt command line to encrypt a directory.
   """
usage="""
   python %prog  [-v] 
   -h for help"""

TRUECRYPT_EXECUTABLE="sudo truecrypt"
import sys
import os
import subprocess
from optparse import OptionParser
import logging
import random
import tempfile
import shutil


#truecrypt has a minimum size for the volume (i found it around 290000 didn't work for me, so i'm setting it to 300000
TC_MIN_SIZE=300000
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

   parser=OptionParser(usage=usage,description=description)
   #general options
   
   parser.add_option("-p"
                        ,"--password"
                        ,default = None
                        , help="Password for the truecrypt volume")
   parser.add_option("-d"
                        ,"--dir"
                        ,default = None
                        , help="Directory to encrypt")
   parser.add_option("-v"
                        ,"--verbose"
                        , default = "INFO"
                        , help="Level of verbose output to Display to stdout (DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)")

   opts,args=parser.parse_args()
   error=None
   if opts.dir is None:
      error = "You must select a directory using -d|--dir"
   if opts.password is None:
      error = "You must enter a password using -p|--password"

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def getRandomFile(dirName):
   filelist = []
   for (path,dirs,files) in os.walk(dirName):
      for file in files:
         filename = os.path.join(path,file)
         filelist.append(filename)
         logging.debug(filename)
   index = random.randint(0,len(filelist)-1)
   return filelist[index]

def getDirSize(dirName):
   #Note: for now, this function may traverse symlinks infinitely
   size = 0
   for (path,dirs,files) in os.walk(dirName):
      for file in files:
         filename = os.path.join(path,file)
         try:
            size += os.path.getsize(filename)
         except OSError, e:
            logging.error("Error: "+str(e))
         logging.debug(filename)
      size += os.path.getsize(path)
      logging.debug(path)
   return size

def tcCreateVolume(filename,password,size,randomFile):
   if size < TC_MIN_SIZE:
      logging.info("Volume size is too small (%s). Setting size to (%s)"%(size,TC_MIN_SIZE))
      size = TC_MIN_SIZE
   cmd = TRUECRYPT_EXECUTABLE
   cmd += " -c"                          #create
   cmd += " --encryption=AES"            #encryption algorithm
   cmd += " --filesystem=FAT"            #filesystem
   cmd += " --hash=SHA-512"              #hash algorithm
   cmd += " -p "+password                #volume password
   cmd += " --random-source="+randomFile #used for encryption strength
   cmd += " --volume-type=normal"        #normal or hidden
   cmd += " --size="+str(int(size))      #volume size
   cmd += " -k ''"                       #keyfiles
   cmd += " "+filename                   #volume file
   logging.debug(cmd)
   logging.info("Creating truecrypt volume: %s"%(filename))
   subprocess.call(cmd,shell=True)

def tcMountVolume(volume,mountpoint,password):
   cmd = TRUECRYPT_EXECUTABLE
   cmd += " -t"
   cmd += " -k"
   cmd += " ''"
   cmd += " --protect-hidden=no"
   cmd += " -p " + password
   cmd += " " + volume
   cmd += " " + mountpoint
   logging.debug(cmd)
   logging.info("Mounting truecrypt volume: %s"%(volume))
   subprocess.call(cmd,shell=True)

def tcDismountVolume(volume):
   cmd = TRUECRYPT_EXECUTABLE
   cmd += " -d"
   cmd += " " + volume
   logging.debug(cmd)
   logging.info("Dismounting truecrypt volume: %s"%(volume))
   subprocess.call(cmd,shell=True)

def tcEncryptDir(path,password):
   #---0. setup
   path = os.path.normpath(path)
   dirName = os.path.basename(path)
   volumeName = dirName+".tc"
   mountPoint = tempfile.mkdtemp()
   logging.debug("Made temporary mount point: "+mountPoint)

   #---1. find the size of the directory
   #we'll add 2% to the file size for the truecrypt header (i'm not sure how much is needed)
   size = getDirSize(path) * 1.02
   #---2. create the truecrypt volume
   tcCreateVolume(volumeName,password,size,getRandomFile(path))
   #---3. mount the truecrypt volume
   tcMountVolume(volumeName,mountPoint,password)
   #---4. copy the files
   shutil.copytree(path,os.path.join(mountPoint,dirName))
   #---5. dismount
   tcDismountVolume(volumeName)
   #---6. cleanup
   shutil.rmtree(mountPoint,ignore_errors=True)

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
                    #format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
                    format='[%(levelname)s]: %(message)s')
					
   return tcEncryptDir(opts.dir,opts.password)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)

