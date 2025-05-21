import wiringpi
#import serial
import RPi.GPIO as GPIO
import time
import math
from Adafruit_MCP230xx.Adafruit_MCP230xx import Adafruit_MCP230XX
from ADS1x15 import ADS1015 as ADS1x15
import Adafruit_MCP3008
import math

class RelayBoards:
      __pinR1 = 0
      __pinR2 = 0
      __pinR3 = 0
      __pinR4 = 0

      def __init__(self, R1, R2, R3=2, R4=3):
         time.sleep(0.01)
         
         GPIO.setmode(GPIO.BCM)
         self.__pinR1 = R1
         self.__pinR2 = R2
         self.__pinR3 = R3
         self.__pinR4 = R4
         
   
      def relayOn(self, n):
         __pinHold = self.getPin(n)
         GPIO.setup(__pinHold, GPIO.OUT)
         GPIO.output(__pinHold, True)

      def relayOff(self, n):
         __pinHold = self.getPin(n)
         GPIO.setup(__pinHold, GPIO.OUT)
         GPIO.output(__pinHold, False)
         
      def relaySet(self, n, s):
         __pinHold = self.getPin(n)
         GPIO.setup(__pinHold, GPIO.OUT)
         if s:
            GPIO.output(__pinHold, True)
         else:
            GPIO.output(__pinHold, False)

      def relayGet(self, n):
         __pinHold = self.getPin(n)
         GPIO.setup(__pinHold, GPIO.IN)
         return GPIO.input(__pinHold)

         
      def getPin(self, n):
         __pinHold = 0
         
         if n == 0:
            __pinHold = self.__pinR1
         elif n == 1:
            __pinHold = self.__pinR2
         elif n == 2:
            __pinHold = self.__pinR3
         else:
            __pinHold = self.__pinR4
         
         return __pinHold

class Buzzer:
      __pin = 0

      def __init__(self, id):
         time.sleep(0.01)
         GPIO.setmode(GPIO.BCM)
         self.__pin = id
         GPIO.setup(self.__pin, GPIO.OUT)
      
      def on(self):
         GPIO.output(self.__pin, True)
         
      def off(self):
         GPIO.output(self.__pin, False)
    
      def set(self,s):
         GPIO.output(self.__pin, s)

class LED:
      __pin = 0

      def __init__(self, id):
         time.sleep(0.01)
         GPIO.setmode(GPIO.BCM)
         self.__pin = id
         GPIO.setup(self.__pin, GPIO.OUT)
      
      def on(self):
         GPIO.output(self.__pin, True)
         
      def off(self):
         GPIO.output(self.__pin, False)
    
      def set(self,s):
         GPIO.output(self.__pin, s)
            
      def toggle(self):
         state = GPIO.input(self.__pin)
         GPIO.output(self.__pin, not state)
            
      def __call__(self):
         return GPIO.input(self.__pin)

class Button:
      __pin = 0

      def __init__(self, id):
         time.sleep(0.01)
         GPIO.setmode(GPIO.BCM)
         self.__pin = id
         GPIO.setup(self.__pin, GPIO.IN)
         
      def __call__(self):
         return GPIO.input(self.__pin)

class Piezo:
      __pin = 0
      isEnabled = False
      driveState = False
      
      def __init__(self, id):
         time.sleep(0.01)
         GPIO.setmode(GPIO.BCM)
         self.__pin = id
         GPIO.setup(self.__pin, GPIO.OUT)
      
      def drive(self):
         if (self.driveState):
            self.driveState = False
         else:
            self.driveState = True
            
         if (self.isEnabled):
            if (self.driveState):
               GPIO.output(self.__pin, True)
            else:
               GPIO.output(self.__pin, False)
      
      def enable(self):
         self.isEnabled = True
      
      def disable(self):
         self.isEnabled = False
         GPIO.output(self.__pin, False)
      
class Switch:
      __pin = 0

      def __init__(self, id):
         time.sleep(0.01)
         GPIO.setmode(GPIO.BCM)
         self.__pin = id
         GPIO.setup(self.__pin, GPIO.IN)
         
      def __call__(self):
         return wGPIO.input(self.__pin)
 
class RgbLedCc:
   __pinR = 0
   __pinG = 0
   __pinB = 0
   colour = [True,True,True]
   
   def __init__(self, r, g, b):
      time.sleep(0.01)
      GPIO.setmode(GPIO.BCM)
      self.__pinR = r
      self.__pinG = g
      self.__pinB = b
      GPIO.setup(self.__pinR, GPIO.OUT)
      GPIO.setup(self.__pinG, GPIO.OUT)
      GPIO.setup(self.__pinB, GPIO.OUT)
            
   def set(self, r, g, b):
      GPIO.output(self.__pinR, r)
      GPIO.output(self.__pinG, g)
      GPIO.output(self.__pinB, b)
      self.colour = [GPIO.input(self.__pinR),
         GPIO.input(self.__pinG),
         GPIO.input(self.__pinB)]
      
   def toggle(self):
      #Toggling the colour on and off. not switching colours
      colourCheck = [GPIO.input(self.__pinR),
         GPIO.input(self.__pinG),
         GPIO.input(self.__pinB)]
      
      if colourCheck == self.colour:
         GPIO.output(self.__pinR, False)
         GPIO.output(self.__pinG, False)
         GPIO.output(self.__pinB, False)
      else:
         GPIO.output(self.__pinR, self.colour[0])
         GPIO.output(self.__pinG, self.colour[1])
         GPIO.output(self.__pinB, self.colour[2])

class RgbLedCa:
   __pinR = 0
   __pinG = 0
   __pinB = 0
   colour = [False,False,False]
   
   def __init__(self, r, g, b):
      time.sleep(0.01)
      GPIO.setmode(GPIO.BCM)
      self.__pinR = r
      self.__pinG = g
      self.__pinB = b
      GPIO.setup(self.__pinR, GPIO.OUT)
      GPIO.setup(self.__pinG, GPIO.OUT)
      GPIO.setup(self.__pinB, GPIO.OUT)
            
   def set(self, r, g, b):
      GPIO.output(self.__pinR, not r)
      GPIO.output(self.__pinG, not g)
      GPIO.output(self.__pinB, not b)
      self.colour = [GPIO.input(self.__pinR),
         GPIO.input(self.__pinG),
         GPIO.input(self.__pinB)]
      
   def toggle(self):
      #Toggling the colour on and off. not switching colours
      colourCheck = [GPIO.input(self.__pinR),
         GPIO.input(self.__pinG),
         GPIO.input(self.__pinB)]
      
      if colourCheck == self.colour:
         GPIO.output(self.__pinR, True)
         GPIO.output(self.__pinG, True)
         GPIO.output(self.__pinB, True)
      else:
         GPIO.output(self.__pinR, self.colour[0])
         GPIO.output(self.__pinG, self.colour[1])
         GPIO.output(self.__pinB, self.colour[2])

class MCP23017:

   def __init__(self):
      try:
         self.setAddress(0x20)
      except:
         pass

   def setAddress(self,address):
      self.mcp = Adafruit_MCP230XX(busnum = 1, address = address, num_gpios = 16)
      
   def pinMode(self, pin, mode):
      self.mcp.config(pin, mode)
      
   def pullUpPin(self, pin):
      self.mcp.pullup(pin, 1)
      
   def digitalWrite(self,pin,value):
      self.mcp.output(pin, value)
      
   def digitalRead(self,pin):
      value = self.mcp.input(pin)
      if value > 0:
         return(1)
      else:
         return(0)
       
class ADS1015:
   def __init__(self):
      self.setAddress(0x48)
      
   def readAnalogue(self,port):
      value = (self.ads.read_adc(port))/(5*100)
      return value
   
   def setAddress(self,address):
      self.ads = ADS1x15(address)
      
class MCP3008:
   def __init__(self, CLK, DOUT, DIN, CS):
      self.mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=DOUT, mosi=DIN)
   
   def analogRead(self,pin):
      value = self.mcp.read_adc(pin)/205
      return(value)
      
#TODO
class RotaryAngleSensor:
   __pin = 0
   full_angle = 0
   
   def __init__(self, id, angle):
      time.sleep(0.01)
      self.__pin = id
      full_angle = angle
      wiringpi.wiringPiSetupGpio()
      wiringpi.pinMode(self.__pin, wiringpi.INPUT)
      
   def readAngle(self):
      return adcval/1024*full_angle
    
   def readRaw(self):
      return adcval()
   
   def adcval(self):
      return wiringpi.analogRead(self.__pin)
    
   def __call__(self, trigger):
      if (readAngle() >= trigger):
         return readAngle()
 
class DCMotorV1:
      dir = 0
      pwm = 0
      brake = 0
      running = False
      
      def __init__(self, d, p, b):
         time.sleep(0.01)
         self.dir = d
         self.pwm = p
         self.brake = b
         self.running = False
         GPIO.setmode(GPIO.BCM)
         
      def __call__(self):
         return self.running
         
      def begin(self):
         GPIO.setup(self.dir, GPIO.OUT)
         GPIO.setup(self.brake, GPIO.OUT)
         GPIO.setup(self.pwm, GPIO.OUT)
         GPIO.output(self.dir, False)
         GPIO.output(self.brake, False)
         
         self.motorPWM = GPIO.PWM(self.pwm, 100)
         self.motorPWM.start(0)
         
      def run(self, direction, speed):
         if (direction == 1):
            GPIO.output(self.dir, True)
         else:
            GPIO.output(self.dir, False)
         
         GPIO.output(self.brake, False)
         self.motorPWM.ChangeDutyCycle(speed)

      def stop(self):
         self.motorPWM.ChangeDutyCycle(100)
         GPIO.output(self.brake, True)
         
      def release(self):
         GPIO.output(self.brake, False)
         self.motorPWM.ChangeDutyCycle(0)
         
class GPS:
   storedData = [0,0]

   def __init__(self):
      self.uart = wiringpi.Serial("/dev/serial0", 9600)
      
   def read(self):
      data = ""
      c = 0
      while True:
         input = self.uart.getchar()
         if input == "\r":
            c = c + 1
         if c > 3:
            return(data)
         data += input
   
   def returnFix(self):
      data = self.read().split('\n')
      for i in range(len(data)):
         if '$GPGGA' in data[i]:
            if data[i].split(',')[2][:2] == '':
               return(False)
            else:
               return(True)
   
   def getPosition(self):
      data = self.read().split('\n')
      latitude = self.storedData[0]
      longitude = self.storedData[1]
      for i in range(len(data)):
         if '$GPGGA' in data[i]: 
            try:
               lat = data[i].split(',')[2]
               lon = data[i].split(',')[4]
               latitude = float(lat[:2])+(float(lat[2:])/60)
               longitude = float(lon[:3])+(float(lon[3:])/60)
               self.storedData = [latitude,longitude]
            except:
               pass
            
      return(latitude,longitude)
      
   def getAltitude(self):
      data = self.read().split('\n')
      
      for i in range(len(data)):
         if '$GPGGA' in data[i]:
            try:
               altitude = float(data[i].split(',')[9])
            except:
               altitude = 0
      return(altitude)
      
   def getSatellites(self):
      data = self.read().split('\n')
      
      for i in range(len(data)):
         if '$GPGGA' in data[i]:
            try:
               satellites = int(data[i].split(',')[7])
            except:
               satellites = 0
      return(satellites)

   def getDistance(self, lon1, lat1, lon2, lat2):

    # convert decimal degrees to radians 
    lon1 = math.radians(lon1)
    lat1 = math.radians(lat1)
    lon2 = math.radians(lon2)
    lat2 = math.radians(lat2)

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371000 #6371 Radius of earth in kilometers. Use 3956 for miles
    return(c * r)
      
   def getBearing(self,lat1,lon1,lat2,lon2):
      lat1 = math.radians(lat1)
      lat2 = math.radians(lat2)

      diffLong = math.radians(lon2 - lon1)

      x = math.sin(diffLong) * math.cos(lat2)
      y = (math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
          * math.cos(lat2) * math.cos(diffLong)))

      initial_bearing = math.atan2(x, y)
      initial_bearing = math.degrees(initial_bearing)
      compass_bearing = (initial_bearing + 360) % 360
      return compass_bearing