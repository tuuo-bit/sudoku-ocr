# !/usr/bin/env python3

#!/usr/bin/env python3

# Modules
from goto import *
import time
import var
import pio
import resource
import sys
import subprocess

# Peripheral Configuration Code (do not edit)
#---CONFIG_BEGIN---
import cpu
import FileStore
import VFP
import camera
import Generic
import Displays

def peripheral_setup () :
# Peripheral Constructors
 pio.cpu=cpu.CPU ()
 pio.storage=FileStore.FileStore ()
 pio.server=VFP.VfpServer ()
 pio.Camera=camera.RPiCamera ()
 pio.ClickButton=Generic.Button (pio.GPIO5)
 pio.Display=Displays.TFTDisplay (pio.GPIO13, pio.GPIO12)
 pio.SolveButton=Generic.Button (pio.GPIO4)
 pio.storage.begin ()
 pio.server.begin (0)
# Install interrupt handlers

def peripheral_loop () :
 pass

#---CONFIG_END---


import RPi.GPIO as g
import os

message_to_proteus = "imageModified.txt"

def create_message( name):
 print( "Creating Message ", name)
 file = open( name, "x")
 #time.sleep( 5)
 while message_to_proteus not in os.listdir():
  print( "Awaiting acknowledgement, processing image")
  time.sleep(5)
 print( "Acknowledgement recieved")
 file.close()
 os.remove(  name)
 os.remove( message_to_proteus)
 print(  name, " and ", message_to_proteus, " cleared")

g.setmode( g.BCM)
g.setup( 5, g.IN) # ClickButton
g.setup( 4, g.IN) # SolveButton

# Main function
def main () :
# Setup
 peripheral_setup()
 pio.Camera.setResolution( 640, 480)
 print( "~ Setup Complete")
# Infinite loop
 while True :
  peripheral_loop()
  if g.input( 5) == True:
   pio.Display.clear()
   pio.Camera.capture( 100)
   pio.Display.loadImage( pio.Camera.getLastImage(), 0)
  if g.input( 4) == True:
   print( os.getcwd())
   create_message( "solveButtonPressed.txt")
   pio.Display.loadImage( pio.Camera.getLastImage(), 0)
   time.sleep(3)
  pass
# Command line execution
if __name__ == '__main__' :
  main()