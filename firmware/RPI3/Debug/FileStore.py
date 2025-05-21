import os
from ReadList import ReadList
from PrintList import PrintList

class FileStore :
   def __init__(self):
      self._cwd = './'
      self._delimiter=','
      pass
   
   def begin(self):
      pass
   
   def _absPath(self, filename):
      if (filename[0] == '/'):
         return filename
      else:
         return self._cwd + filename;
   
   def __call__(self, filename):
      try:
         file = open(self._absPath(filename), 'r')
         if (file == None):
            return False
         file.close()
         return True
      except OSError:
         return False
   
   def open(self, filename, mode='r'):
      try:
         return open(self._absPath(filename), mode)
      except OSError:
         return None
   
   def close(self, file):
      if (file != None):
         file.close()
   
   def flush(self, file):
      return file.flush()
   
   def remove(self, filename):
      return os.remove(self._absPath(filename))
   
   def chdir(self, dir):
      self._cwd = self._absPath(dir) + '/'
   
   def mkdir(self, dir):
      return os.makedirs(self._absPath(dir), exist_ok=True)
   
   def rmdir(self, dir):
      return os.rmdir(self._absPath(dir))
   
   def setDelimiter(self, delimiter):
      self._delimiter = delimiter
   
   def write(self, file, *args):
      def writeString(s):
         nonlocal file
         file.write(s)
      list = PrintList(writeString)
      list.setDelimiter(self._delimiter)
      list.print(*args)

   def writeln(self, file, *args):
      self.write(file, *args)
      file.write("\n")

   def readln(self, file):
      return file.readline()

   def read(self, file, output=[]):
      def readChar():
         nonlocal file
         return file.read(1)
      list = ReadList(readChar)
      list.setDelimiter(self._delimiter)
      list.read(output)

   def flush(self, file):
      file.flush()

   def print(self, file, *args):
      if args:
         file.write(self._delimiter.join(str(x) for x in args))

   def println(self, file, *args):
      if args:
         file.write(self._delimiter.join(str(x) for x in args))
      file.write("\n")
   