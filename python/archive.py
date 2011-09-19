#!/usr/bin/python
import os
import datetime,time

#"""
rootDir="/mnt/thttpd/tombaBuildShare"
archiveDir="/mnt/archives/tombaBuildShare"
"""
rootDir="/mnt/archives/tombaBuildShare"
archiveDir="/mnt/archives/tombaBuildShare2"
#"""
age=30 #in days

baseDate = datetime.date.today() - datetime.timedelta(days=age)
excludeDirs=['TombaTkDoc']
#get a list of all the files
oldFiles = []
for root,dirs,files in os.walk(rootDir):
  for file in files:
    fullFilePath = os.path.join(root,file)
    year,month,day = time.localtime(os.stat(fullFilePath).st_mtime)[:3]
    lastUsed = datetime.date(year,month,day)
    if lastUsed < baseDate:
      for exDir in excludeDirs:
        if not fullFilePath.find(os.sep+exDir+os.sep) > 0:
          oldFiles.append(fullFilePath)

for file in oldFiles:
  src = file
  dst = file.replace(rootDir,archiveDir)
  dstDir = os.path.dirname(dst)
  if not os.path.exists(dstDir):
    os.makedirs(dstDir)
