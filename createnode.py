#!/usr/bin/python
import os
import sys

# Creates a new openvz container for the new csee environment.
# Creates:
#  -Config File
#  -Container Root
#  -Adds network config

# The only argument this command takes is a config file, and it
# defaults to a file called nodeconf in the active directory.
# This allows cfengine to easily configure and use this script.

def readConfig(configFile):
  containers = []
  return containers

def createRoot(container):
  #Clone zfs template
  #Success return true, else false

def configNetwork(container):
  #Configure /etc/sysconfig/ifcfg-eth0
  #Configure /etc/sysconfig/network
  #Copy configs over to cfengine
  #Success return true, else false

def update(container):
  #Runs updaterpm inside of the container
  #Returns True on success, else False

def cfengine(container):
  #Runs cfengine with the proper configuration for this zone before booting
  #

def main():
  if len(argv) >= 2:
    configFile = argv[1]
  else:
    configFile = "./nodeconf"
  

main()
