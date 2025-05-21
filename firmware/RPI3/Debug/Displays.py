import Adafruit_ILI9341
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from PIL import Image, ImageDraw, ImageFont
import smbus
from PrintList import PrintList
import time
import sys


class TFTDisplay:  
   def __init__(self, DC, RST):
         SPI_PORT    = 0
         SPI_DEVICE  = 0
         Speed       = 64000000
         Pi          = SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=Speed)
         
         #Setup Display
         self.disp = Adafruit_ILI9341.ILI9341(DC,rst=RST, spi=Pi)
         
         #Start Display
         self.disp.begin()
         
         #Setup for drawing
         self.draw = self.disp.draw()
         
         #Setup Colours
         self.redFill = 0
         self.greenFill = 0
         self.blueFill = 0
         self.redLine = 0
         self.greenLine = 0
         self.blueLine = 0
         
         #Setup Text Properties
         self.font = ImageFont.load_default()
         self.textSize = 90
   
   def loadImage(self,Picture,angle):
      try:
         self.image = Image.open(Picture)
         self.image = self.image.rotate(angle)
         self.image = self.image.resize((240, 320)) # sets the image size. Needed for all
         self.disp.display(self.image)
      except:
         print("Image name incorrect, or incorrect format", file=sys.stderr)
   
   #Drawing Methods
   
   def setOutline(self,red,green,blue):
      self.redLine = red
      self.greenLine = green
      self.blueLine = blue
   
   def setFill(self,red,green,blue):
      self.redFill = red
      self.greenFill = green
      self.blueFill = blue
      
   def fillScreen(self):
      self.disp.clear((self.redFill,self.greenFill,self.blueFill))
      self.disp.display()
      
   def drawCircle(self,x,y,radius):
      outColour = (self.redLine,self.greenLine,self.blueLine)
      fillColour = (self.redFill,self.greenFill,self.blueFill) 
      self.draw.ellipse((x-radius, y-radius, x+radius, y+radius), outline=outColour, fill=fillColour)
      self.disp.display()
      
   def drawEllipses(self,x,y,width,height):
      outColour = (self.redLine,self.greenLine,self.blueLine)
      fillColour = (self.redFill,self.greenFill,self.blueFill)
      self.draw.ellipse((x-width, y-height, x+width, y+height), outline=outColour, fill=fillColour)
      self.disp.display()
      
   def drawRectangle(self,x,y,height,width):
      outColour = (self.redLine,self.greenLine,self.blueLine)
      fillColour = (self.redFill,self.greenFill,self.blueFill)
      self.draw.rectangle((x, y,x+width ,y+height), outline=outColour, fill=fillColour)
      self.disp.display()
      
   def drawLine(self,x1,y1,x2,y2):
      outColour = (self.redLine,self.greenLine,self.blueLine)
      self.draw.line((x1, y1, x2, y2), fill=outColour)
      self.disp.display()
      
   def newPolygon(self,x,y):
      self.polygon = []
      self.polygon.append((x,y))

   def addPolygonPoint(self,x,y):
      self.polygon.append((x,y))
   
   def drawPolygon(self):
      outColour = (self.redLine,self.greenLine,self.blueLine)
      fillColour = (self.redFill,self.greenFill,self.blueFill)
      self.draw.polygon(self.polygon, outline=outColour, fill=fillColour)
      self.disp.display()
   
   #Text Methods
   
   def draw_rotated_text(self, image, text, position, angle, font, fill):
      # Get rendered font width and height.
      draw = ImageDraw.Draw(image)
      width, height = draw.textsize(text, font=font)
      # Create a new image with transparent background to store the text.
      textimage = Image.new('RGBA', (width, height), (0,0,0,0))
      # Render the text.
      textdraw = ImageDraw.Draw(textimage)
      textdraw.text((0,0), text, font=font, fill=fill)
      # Rotate the text image.
      rotated = textimage.rotate(angle, expand=1)
      # Paste the text into the image, using it as a mask for transparency.
      image.paste(rotated, position, rotated)
   
   def setTextFont(self, size, font):
      fonts = ['DejaVuSerif.ttf','DejaVuSans.ttf','DejaVuSansMono.ttf']
      self.font = ImageFont.truetype(fonts[font], size)

   def customTextFont(self, size, font):
      self.font = ImageFont.truetype(font, size)
   
   def drawText(self, text, x, y, angle):
      fillColour = (self.redFill,self.greenFill,self.blueFill)
      self.draw_rotated_text(self.disp.buffer, text, (x, y), angle, self.font, fill=fillColour)
      self.disp.display()
   
   def clear(self):
      self.disp.clear((255,255,255))
      self.disp.display()
      

class I2CLDC(PrintList): 
   def __init__(self):
      PrintList.__init__(self, self._print)
      self.bus = smbus.SMBus(1)
      self.bus.write_i2c_block_data(62, 128, [1])
      time.sleep(.05)
      self.bus.write_i2c_block_data(62, 128, [12])
      self.bus.write_i2c_block_data(62, 128, [40])
   

   def _print(self,value):
      line = True
      for i in range(len(value)):
         if (i > 16) and line:
            self.bus.write_i2c_block_data(62, 128, [192])
            line = False
            
         try: 
            ascii = ord(value[i])
         except:
            ascii = 63
         self.bus.write_i2c_block_data(62, 64, [ascii])

   def println(self,value):
      self.bus.write_i2c_block_data(62, 128, [192])
      for i in range(len(value)):
         try: 
            ascii = ord(value[i])
         except:
            ascii = 63
         self.bus.write_i2c_block_data(62, 64, [ascii])
         
   def clear(self):
      self.bus.write_i2c_block_data(62, 0, [1])
      