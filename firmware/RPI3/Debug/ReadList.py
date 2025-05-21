# ReadList Class
from datetime import datetime
class ReadList:
   def __init__(self, readHandler):
      self._delimiter = ""
      self._readHandler = readHandler
      self._base = 10

   def setDelimiter(self, delimiter):
      self._delimiter = delimiter

   def read(self, output = []):
      for i in range(len(output)):
         s = self._readNext()
         if isinstance(output[i], int):
            output[i] = int(s)
         elif isinstance(output[i], str):
            output[i] = s
         elif isinstance(output[i], datetime):
            output[i] = datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

   def setPlaces(self,Places):
      pass

   def setBase(self,Base):
      self._base = Base

   def _readNext(self):
      s = "";
      while True:
         c = self._readHandler()
         if not c or c == self._delimiter or c == "\r":
            return s
         s += c
