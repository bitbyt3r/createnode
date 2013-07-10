#!/usr/bin/python
import re
import os
import sys
import ConfigParser

# Creates a new openvz container for the new csee environment.
# Creates:
#  -Config File
#  -Container Root
#  -Adds network config

# The only argument this command takes is a config file, and it
# defaults to a file called nodeconf in the active directory.
# This allows cfengine to easily configure and use this script.

# In general, this script is only run on the root node.

def readConfig(configFile):
  containers = {}
  config = ConfigParser.ConfigParser()
  if not(os.path.isfile(configFile)):
    sys.exit("The config file "+configFile+" is not a file. That is unfortunate.")
  if config.read(configFile):
    sections = {}
    for i in config.sections():
      sections[i] = config.items(i)
  else:
    sys.exit("Config File is not valid.")
  if "main" in sections.keys():
    options = {}
    for i in sections["main"]:
      options[i[0]] = i[1]
  else:
    options = None
    print "No global options found. Strange. I might explode."
  for i in sections.keys():
    if not i == "main":
      containers[i] = {}
      for j in sections[i]:
        containers[i][j[0]] = j[1]
      if not "section" in containers[i].keys():
        containers[i]["section"] = i
  print containers, options
  if options:
    replaceKeys(options, {})
  containers = [replaceKeys(containers[x], options) for x in containers]
  return containers, options

def replaceKeys(container, main):
  if main:
    for i in main.keys():
      if not i in container.keys():
        container[i] = main[i]
  madeProgress = True
  keysWithSubs = remainingSubs(container)
  while keysWithSubs and madeProgress:
    madeProgress = False
    for j in keysWithSubs.keys():
      if not any(map(lambda x: x in keysWithSubs.keys(), keysWithSubs[j])):
        for k in keysWithSubs[j]:
          container[j] = re.sub("<"+k+">", container[k])
          madeProgress = True
    keysWithSubs = remainingSubs(container)
  
def remainingSubs(container):
  keysWithSubs = {}
  for i in container.keys():
    if re.findall(".*<(.+?)>.*", container[i]):
      keysWithSubs[i] = re.findall(".*<(.+?)>.*", container[i])
  return keysWithSubs

def createRoot(container):
  #Clone zfs template
  #Success return true, else false
  return

def configNetwork(container):
  #Configure /etc/sysconfig/ifcfg-eth0
  #Configure /etc/sysconfig/network
  #Copy configs over to cfengine
  #Success return true, else false
  return

def update(container):
  #Runs updaterpm inside of the container
  #Returns True on success, else False
  return

def cfengine(container):
  #Runs cfengine with the proper configuration for this zone before booting
  #
  return

def main():
  if len(sys.argv) >= 2:
    configFile = sys.argv[1]
  else:
    configFile = "./nodeconf"
  containers, options = readConfig(configFile)
  print containers, options
  

main()
