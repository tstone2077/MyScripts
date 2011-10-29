#!/usr/bin/python
"""
  OriginalAuthor: Thurston Stone <tstone2077@gmail.com>
  Description: Script to send an email if the external ip address changes
  Usage: emailIP.py -h for help 
"""

LOG_MESSAGE_PREFIX = "emailIP.py"
cmd_desc="""
   Script to send an email if the external ip address changes
   """
cmd_usage="""
   python %prog [-v level] [-c configfile] [-t to_email] [-f from_email] [-i expected_ip] [-s]
   -h for help"""

import sys
import os
from optparse import OptionParser
import logging
import urllib2
import smtplib
from email.mime.text import MIMEText
from ConfigParser import SafeConfigParser


INVALID_USAGE_RETURN_CODE = 2
INVALID_INPUTS = 3

try:
   LOG_MESSAGE_PREFIX = os.path.basename(os.path.abspath(__file__))
except:
   pass
   

class InvalidInputs(Exception): 
  def __init__(self,error):
    self.error=error
  def __str__(self):
    return self.error
  def printError(self):
    print "ERROR: ",self.error

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
   
   parser.add_option("-i"
                        ,"--ip"
                        , default = None
                        , help="expected ip.  If the current ip is different, an email will be sent")
   parser.add_option("-t"
                        ,"--toEmail"
                        , default = None
                        , help="email address to send a mail if the ip has changed")
   parser.add_option("-f"
                        ,"--fromEmail"
                        , default = None
                        , help="email address from which to send a mail if the ip has changed")
   parser.add_option("-s"
                        ,"--save"
                        , default = False
                        , action="store_true"
                        , help="Save the settings to the config file if --ipor --email are entered")
   parser.add_option("-c"
                        ,"--config"
                        , default = os.path.join(os.path.expanduser("~"),".emailIP")
                        , help="Location of the config file.")
   parser.add_option("-v"
                        ,"--verbose"
                        , default = "INFO"
                        , help="Level of verbose output to Display to stdout (DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)")

   opts,args=parser.parse_args()
   error=None

   if error is not None: raise InvalidUsage(parser,error)
   return opts,args

def emailIP(configfile,toEmail = None, fromEmail = None, expectedIP = None, save = True):
    parser = SafeConfigParser()
    try:
       parser.read(configfile)
       if not expectedIP:
          expectedIP = parser.get("emailIP","expectedip")
       if not fromEmail:
          fromEmail  = parser.get("emailIP","fromemail")
       if not toEmail:
          toEmail  = parser.get("emailIP","toemail")
    except:
       pass

    error = None
    if not toEmail:
       error = "toEmail is not set"
    if not fromEmail:
       error = "fromEmail is not set"
    if not expectedIP:
       error = "expectedIP is not set"
    if error:
       raise InvalidInputs(error)
    
    if not parser.has_section("emailIP"):
       parser.add_section("emailIP")
    parser.set("emailIP","fromEmail",fromEmail)
    parser.set("emailIP","toEmail",toEmail)
    parser.set("emailIP","expectedIP",expectedIP)
    currentIP = urllib2.urlopen("http://www.whatismyip.org").readlines()[0]
    if currentIP != expectedIP:
       logging.info( "%s != %s"%(currentIP,expectedIP))
       msg = MIMEText("IP Changed from %s to %s"%(expectedIP,currentIP))
       msg['Subject'] = "New IP: %s"%currentIP
       msg['From'] = fromEmail
       msg['To'] = toEmail
       s = smtplib.SMTP('localhost')
       s.sendmail(fromEmail,[toEmail],msg.as_string())
       parser.set("emailIP","expectedIP",currentIP)
       fp = open(configfile,"w")
       parser.write(fp)
       fp.close()
    if save:
       fp = open(configfile,"w")
       parser.write(fp)
       fp.close()

def main():
   """  
      The main function.  This function will run if the command line is called as 
      opposed to this file being imported.
   """
   opts,args=validateArgs()
   level=getattr(logging,opts.verbose.upper())
   logging.basicConfig(level=level,
                    format= '' + LOG_MESSAGE_PREFIX + ':[%(asctime)s]:[%(levelname)s]: %(message)s')
					
   return emailIP(opts.config,opts.toEmail,opts.fromEmail,opts.ip,opts.save)

# if this program is run on the command line, run the main function
if __name__ == '__main__':
   try:
      sys.exit(main())
   except InvalidUsage,e:
      e.printError()
      sys.exit(INVALID_USAGE_RETURN_CODE)
   except InvalidInputs,e:
      e.printError()
      sys.exit(INVALID_INPUTS)

