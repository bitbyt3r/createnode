#!/usr/bin/python
import re
import os
import sys
import ConfigParser
import socket

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
  if options:
    options = replaceKeys(options, {})
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
          if k in container.keys():
            container[j] = re.sub("<"+k+">", container[k], container[j])
            madeProgress = True
    keysWithSubs = remainingSubs(container)
  return container
  
def remainingSubs(container):
  keysWithSubs = {}
  for i in container.keys():
    if re.findall(".*<(.+?)>.*", container[i]):
      keysWithSubs[i] = re.findall(".*<(.+?)>.*", container[i])
  return keysWithSubs

def createRoot(container, options):
  #Clone zfs template
  #Success return true, else false
  print "Creating private dir for:", container['name'], "...",
  if os.path.isdir(container['remote_private_dir']):
    print "\t[\033[31mFailed\033[0m]"
    print "There is already a directory at:", container['remote_private_dir']
    return False
  if os.system("/sbin/zfs clone "+container['base_node']+" "+container['remote_zfs_pool']):
    print "\t[\033[31mFailed\033[0m]"
    print "ZFS cloning failed. Are you allowed to do this?"
    return False
  print "\t[\033[32m  Ok  \033[0m]"
  return True

def configNetwork(container, options):
  #Configure /etc/sysconfig/ifcfg-eth0
  #Configure /etc/sysconfig/network
  #Copy configs over to cfengine
  #Success return true, else false
  print "Configuring network for:", container['name'], "...",
  with open(container['remote_private_dir']+"/etc/sysconfig/network-scripts/ifcfg-eth0", "w") as ifcfg:
    ifcfg.write("DEVICE=eth0\n")
    ifcfg.write("BOOTPROTO=static\n")
    ifcfg.write("ONBOOT=yes\n")
    ifcfg.write("IPADDR="+container['ip_address']+"\n")
    ifcfg.write("BROADCAST="+container['broadcast']+"\n")
    ifcfg.write("NETMASK="+container['netmask']+"\n")
    ifcfg.write("HOSTNAME="+container['hostname']+"\n")
    ifcfg.write("GATEWAY="+container['gateway']+"\n")
  with open(container['remote_private_dir']+"/etc/sysconfig/network", "w") as network:
    network.write("NETWORKING=yes\n")
    network.write("GATEWAYDEV=venet0\n")
    network.write("NETWORKING_IPV6=no\n")
    network.write("IPV6_DEFAULTDEV=venet0\n")
    network.write("NISDOMAIN=CSEEfoo\n")
    network.write("GATEWAY="+container['gateway']+"\n")
    network.write("HOSTNAME="+container['hostname']+"\n")
  print "\t[\033[32m  Ok  \033[0m]"
  return True

def update(container, options):
  #Runs updaterpm inside of the container
  #Returns True on success, else False
  print "Running rpmupdate on:", container['name'], "...",
  print "\t[\033[32m  Ok  \033[0m]"
  return True

def cfengine(container, options):
  #Runs cfengine with the proper configuration for this zone before booting
  #
  print "Running cfengine on:", container['name'], "...",
  print "\t[\033[32m  Ok  \033[0m]"
  return True

def cleanRoot(container, options):
  return True

def cleanNetwork(container, options):
  return True

def main():
  if len(sys.argv) >= 2:
    configFile = sys.argv[1]
  else:
    configFile = "./nodeconf"
  containers, options = readConfig(configFile)
  if socket.gethostname() != options['root_server']:
    print "You appear to be running on a machine other than the root server."
    response = raw_input("Are you sure you know what you are doing? [Y/n]:")
    if not response in ["y", "Y", "yes", "Yes", ""]:
      sys.exit("Try running this script again on: "+options['root_server'])
  for i in containers:
    error = False
    for func in [createRoot, configNetwork, update, cfengine]:
      if not(func(i, options)):
        error = True
        break
    if error:
      cleanRoot(i, options)
      cleanNetwork(i, options)
      sys.exit("Failed!")
    print "Successfully created:", i['name']
  print "Finished creating nodes successfully."  

main()
