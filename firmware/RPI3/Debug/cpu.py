# Raspberry Pi CPU Module
# It provides access to the GPIO pins
import time
import pio
import RPi.GPIO as GPIO

try:
   import pygame
except:
   print("No pygame")
import subprocess

# Constants
#PINMODE
INPUT = 0
OUTPUT = 1
PWM = 2

#PULLUP
PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2

class CPU:
   # Constructor
   def __init__(self) :
      self.PWMsignals = {}
      GPIO.setmode(GPIO.BCM)
      try:
         pygame.mixer.init()
      except:
         pass

   # Methods   
   def pinMode(self, pin, mode) :
      if pin in self.PWMsignals:
         self.PWMsignals.pop(pin)
      if mode == OUTPUT :
         GPIO.setup(pin, GPIO.OUT)
      else:
         GPIO.setup(pin, GPIO.IN)

   def pwmMode(self, pin, frequency):   
      GPIO.setup(pin, GPIO.OUT)
      self.PWMsignals.update({pin:GPIO.PWM(pin, frequency)})

   def pullUpDnControl(self, pin, mode) :
       if mode == PUD_OFF :
          GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
       else :
          if mode == PUD_UP:
             GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
          else :
             GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
      
   def digitalWrite(self, pin, state) :
      GPIO.output(pin, state)
      
   def digitalRead(self, pin) :
      return GPIO.input(pin)
      
   def pwmWrite(self, pin, percent):
      if percent != 0:
         self.PWMsignals[pin].start(percent)
      else:
         self.PWMsignals[pin].stop()

   def playSound(self, file):
      pygame.mixer.music.load(file)
      pygame.mixer.music.play()

   def sys(self, *args):
      subprocess.run(args, shell=True)

   def millis(self):
      return int(round(time.time() * 1000))

   def debug(self, *args):
      if args:
         _delimiter = ","
         print(_delimiter.join(str(x) for x in args))
         
pio.IO0 = 0
pio.IO1 = 1
pio.IO2 = 2
pio.IO3 = 3
pio.IO4 = 4
pio.IO5 = 5
pio.IO6 = 6
pio.IO7 = 7
pio.IO8 = 8
pio.IO9 = 9
pio.IO10 = 10
pio.IO11 = 11
pio.IO12 = 12
pio.IO13 = 13
pio.IO14 = 14
pio.IO15 = 15
pio.IO16 = 16
pio.IO17 = 17
pio.IO18 = 18
pio.IO19 = 19
pio.IO20 = 20
pio.IO21 = 21
pio.IO22 = 22
pio.IO23 = 23
pio.IO24 = 24
pio.IO25 = 25
pio.IO26 = 26
pio.IO27 = 27
pio.IO28 = 28
pio.IO29 = 29
pio.IO30 = 30
pio.IO31 = 31
pio.GPIO0 = 0
pio.GPIO1 = 1
pio.GPIO2 = 2
pio.GPIO3 = 3
pio.GPIO4 = 4
pio.GPIO5 = 5
pio.GPIO6 = 6
pio.GPIO7 = 7
pio.GPIO8 = 8
pio.GPIO9 = 9
pio.GPIO10 = 10
pio.GPIO11 = 11
pio.GPIO12 = 12
pio.GPIO13 = 13
pio.GPIO14 = 14
pio.GPIO15 = 15
pio.GPIO16 = 16
pio.GPIO17 = 17
pio.GPIO18 = 18
pio.GPIO19 = 19
pio.GPIO20 = 20
pio.GPIO21 = 21
pio.GPIO22 = 22
pio.GPIO23 = 23
pio.GPIO24 = 24
pio.GPIO25 = 25
pio.GPIO26 = 26
pio.GPIO27 = 27
pio.GPIO28 = 28
pio.GPIO29 = 29
pio.GPIO30 = 30
pio.GPIO31 = 31
#SPI
pio.CLK=11
pio.CS=8
pio.MOSI=10
pio.MISO=9
#I2C
pio.SDA=2
pio.SCL=3
