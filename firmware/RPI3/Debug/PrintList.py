# Printlist Class
from datetime import datetime
class PrintList:
   def __init__(self, handler):
      self._delimiter = ""
      self._handler = handler
      self._base = 10
      self._place = 10
   
   def setDelimiter(self, delimiter):
      self._delimiter = delimiter

   def print(self, *args):
      if args:
         self._handler(self._delimiter.join(self.toString(x) for x in args))

   def println(self, *args):
      if args:
         self._handler(self._delimiter.join(self.toString(x) for x in args) + "\\n")
         
   def setPlaces(self,Places):
      self._place = Places
      
   def setBase(self,Base):
      self._base = Base
      
   def toString(self, object):
      if isinstance(object, datetime):
         return object.strftime("%Y-%m-%d %H:%M:%S.%f")
      _val = str(object)
      
      try:
         if self._base != 10 and isinstance(float(_val), float):
            _val = str(int(float(_val)))
      except:
         pass
      
      if _val.isnumeric():
         if self._base == 2:
            return bin(int(_val)).replace('0b','')
         if self._base == 8:
            return oct(int(_val)).replace('0o','')
         if self._base == 10:
            return _val
         if self._base == 16:
            return hex(int(_val)).replace('0x','')
      else:
         try:
            _val = ("%." + str(self._place) + "f") % float(_val)
         except:
            pass
      return _val
