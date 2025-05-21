# VFP Server
import os, sys, stat, select
import socket, select, struct
import threading
import time, calendar
import re
import VFP
import zeroconf

class Watchdog:
   def __init__(self, timeout, handler):
      self._timeout = timeout
      self._handler = handler
      self._timeoutTime = -1
      self._due = False
   
   def reset(self):
      self._timeoutTime = self._getTime() + self._timeout
      self._due = False
      
   def start(self):
      self._timeoutTime = self._getTime() + self._timeout
      self._due = False
      
   def stop(self):
      self._timeoutTime = -1
      self._due = False
      
   def isDue(self):
      return self._due
      
   def poll(self):
      if self._timeoutTime > 0:
         now = self._getTime()
         if now >= self._timeoutTime:
            self._due = True
            self._timeoutTime = now + self._timeout
            if self._handler:
               self._handler()
               
   # Time in seconds
   def _getTime(self):
      from datetime import datetime
      dt = datetime.now()
      return ((dt.hour * 60) + dt.minute) * 60 + dt.second + dt.microsecond / 1000000.0

class VfpServer:
   
   currentIPAddress = None
   currentUserAgent = None
   
   def __init__(self):
      self.HOST = ''                # Symbolic name meaning all available interfaces
      self.PORT = 8081              # Arbitrary non-privileged port
      self.BUFFERSIZE = 4096

      self.PANEL_SVG = "./panel.svg"
      self.LOG_NAME = "./server.log"
      self.RESOURCE_DIR = "./"

      self.applianceName = ""
      self.clientAddress = None
      self.statusSocket = None
      self.statusBuffer = ""
      self.sessionState = {}
      self.sessionHistory = {}

      KEEPALIVE_INTERVAL = 10
      KEEPALIVE_TIMEOUT  = 30

      self.keepaliveTimer = Watchdog(KEEPALIVE_INTERVAL, self.keepaliveDue)
      self.statusTimeout = Watchdog(KEEPALIVE_TIMEOUT, self.lostStatus)
      
   def processRequest (self, conn, addr) :
         firstLine = ""
         rangeLine = ""
         rangeStart = None
         rangeEnd = None
         currentLine = ""
         lines = [];
         done = False
         etag = ""
         userAgent = ""
         
         #self.writelog("Receiving...")
         conn.settimeout(5.0)

         connfile=conn.makefile('r', 1, encoding="utf8")

         while not done:
            try:
               data = connfile.readline()
               currentLine = data.split('\r')[0]
               currentLine = currentLine.split('\n')[0]
               if currentLine != "":
                  if currentLine.startswith("User-Agent"):
                     self.writelog(currentLine)
                     userAgent = currentLine[12:]
                  if currentLine.startswith("Range"):
                     self.writelog(currentLine)
                     rangeLine = currentLine
                  if currentLine.startswith("If-None-Match"):
                     etag = currentLine[15:]
                  lines.append(currentLine)
               elif firstLine == "":
                  firstLine = lines[0]
                  done = firstLine.startswith('GET') or firstLine.startswith('HEAD')
                  body = len(lines)
               else:
                  done = True
            except socket.timeout:
               self.writelog("Socket Timeout")
               print("socket timeout")
               conn.close()
               return
            except:
               VFP.authorize(False)
               print("socket error")
               self.writelog("Socket Error")
               conn.close()
               return

         conn.settimeout(None)

         if firstLine != "":
            self.writelog(firstLine)
            action = firstLine.split(' ')[0];
            if action=='GET':
               filename = firstLine.split(' ')[1];
               if filename == '/' :
                  #Process a page reload.
                  if self.clientAddress == None or ("Proteus" in str(self.currentUserAgent)) or (self.clientAddress == addr and self.currentUserAgent == userAgent):
                     # If this is a new connection, or a reload from the same client then this is processed normally:
                     filename = 'panel.htm'
                     self.writelog("Client Address:"+str(addr))
                     #print(self.currentIPAddress,addr)
                     #Authorisation dealing with reload addresses
                     if self.currentIPAddress != addr or self.currentUserAgent != userAgent:
                        # print('Changing Ip Address or agent')
                        VFP.authorize(False)
                        self.currentIPAddress = addr
                        self.currentUserAgent = userAgent
                     
                     VFP.callReloadHandlers()

                     # Close any previous status connection and launch the status timeout. Anything that doesn't establish a
                     # status connection within the status timeout period will thus be disconnected.
                     self.clientAddress = addr
                     self.currentUserAgent = userAgent
                     self.statusBuffer = ""
                     self.closeStatus()
                  else:
                     # If an attempt is made to connection from another client without first closing the other, then send a 403:
                     conn.sendall("HTTP/1.1 403 FORBIDDEN\n".encode())
                     conn.sendall("Content-Type: text/html\n\n".encode())
                     conn.sendall("<html>".encode())
                     conn.sendall("<head><title>Appliance In Use</title></head>".encode())
                     conn.sendall("<body><h1>".encode())
                     conn.sendall(("The '"+self.applianceName+"' is under the control of another client ["+str(self.clientAddress)+"].\n").encode())
                     conn.sendall("</h1></body>".encode())
                     conn.sendall("</html>".encode())
                     conn.close()
                     self.writelog("Rejected connection from " +str(addr))
                     return

               elif filename == '/status':
                  #Process a status request.
                  if self.clientAddress == addr and self.currentUserAgent == userAgent:
                     #We send a response header but then keep the connection
                     #open until we receive something to send to it from the Arduino
                     conn.sendall("HTTP/1.1 200 OK\n".encode())
                     conn.sendall("Content-Type: text/plain\n".encode())
                     conn.sendall("Connection: close\n".encode())
                     conn.sendall("\n".encode())
                     if len(self.statusBuffer) == 0:
                        self.openStatus(conn)
                     else:
                        conn.sendall(self.statusBuffer.encode())
                        conn.close()
                        self.statusBuffer = ""
                  else:
                     # Another client is trying to use the appliance:
                     self.writelog("Rejected client:"+str(addr))
                     conn.sendall("HTTP/1.1 403 FORBIDDEN\n".encode())
                     conn.sendall("Content-Type: text/plain\n".encode())
                     conn.sendall("Connection: close\n".encode())
                     conn.sendall("\n\n".encode())
                     conn.close();
                  return
               elif filename == '/session':
                  if self.clientAddress == addr and self.currentUserAgent == userAgent:
                     #Process a session state request.
                     self.openStatus(conn)
                     self.sendState(conn)
                     self.closeStatus()
                  else:
                     # Another client is trying to use the appliance:
                     self.writelog("Rejected client:"+str(addr))
                     conn.sendall("HTTP/1.1 403 FORBIDDEN\n".encode())
                     conn.sendall("Content-Type: text/plain\n".encode())
                     conn.sendall("Connection: close\n".encode())
                     conn.sendall("\n\n".encode())
                     conn.close();
                  return
               elif filename.startswith('/'):
                  filename = filename[1:]       
               if rangeLine != "":
                  m = re.match("[^=]*=([0-9]*)-([0-9]*)", rangeLine)
                  if m != None and len(m.group(1)) > 0:
                     rangeStart = int(m.group(1))
                  if m != None and len(m.group(2)) > 0:                     
                     rangeEnd = int(m.group(2))                                   
               self.sendFile(conn, filename, rangeStart, rangeEnd, etag)

            elif action=='POST' or action=='PUT' :
               if self.clientAddress == addr and self.currentUserAgent == userAgent:
                  # Process messages from the client/browser.
                  # POST messages are passed on to the AVR, PUT messages merely update the session state.
                  conn.sendall("HTTP/1.1 200 OK\n".encode())
                  conn.sendall("Content-Type: text/plain\n".encode())
                  conn.sendall("Connection: close\n".encode())
                  conn.sendall("\n".encode())
                  for i in range(body, len(lines)):
                     currentLine = lines[i]
                     self.writelog(currentLine)
                     if len(currentLine) > 0:
                        if action=='POST':
                           self.writelog("EVENT:"+currentLine)
                           VFP.callEventHandlers(currentLine)
                        else:
                           self.writelog("RECORD:"+currentLine)
                        self.saveState(currentLine)
               else:
                  # Another client is trying to use the appliance:
                  self.writelog("Rejected client:"+str(addr))
                  conn.sendall("HTTP/1.1 403 FORBIDDEN\n".encode())
                  conn.sendall("Content-Type: text/plain\n".encode())
                  conn.sendall("Connection: close\n".encode())
                  conn.sendall("\n\n".encode())
                  conn.close();



         conn.close()

   #Opens a requested file
   def sendFile (self, conn, filename, start, end, etag):
      #Records server acknowledgement
      self.writelog("Sending file '"+filename+"'")       

      #Tries to send the file
      
      #Cache control
      try:
         mtime = str(os.path.getmtime(filename))
         if start == None and end == None and len(etag) > 0 and etag == mtime:
            conn.sendall("HTTP/1.1 304 Not Modified\n\n".encode())
            self.writelog("Cached")
            return
      except:
         mtime = ""

         
      try:
         file = open(self.RESOURCE_DIR + filename, "rb")

      except:
         file = None
         conn.sendall("HTTP/1.1 404 Not Found\n".encode())
         conn.sendall("Content-Type: text/html\n\n".encode())
         conn.sendall("<html>".encode())
         conn.sendall("<head><title> 404 NOT FOUND </title></head>".encode())
         conn.sendall("<body><h1>".encode())
         conn.sendall((filename+" - file not found").encode())
         conn.sendall("</h1></body>".encode())
         conn.sendall("</html>".encode())
         self.writelog("File failed to send\n")

      if file != None:
         data = file.read()
         if start == None and end == None:
            conn.sendall("HTTP/1.1 200 OK\n".encode())
            conn.sendall(("Content-Type: " + self.fileType(filename) + "\n").encode())
            conn.sendall("Accept-Ranges: bytes\n".encode())
            conn.sendall("Connection: close\n".encode())
            conn.sendall("Cache-Control: no-cache\n".encode())
            if len(mtime) > 0:
               conn.sendall(("ETag: " + mtime + "\n").encode())
            conn.sendall(("Content-Length: "+str(len(data))+"\n\n").encode())
            conn.sendall(data) 
            self.writelog("Transfer successful")
         else:   
            conn.sendall("HTTP/1.1 206 OK\n".encode())
            conn.sendall("Accept-Ranges: bytes\n".encode())
            conn.sendall("Connection: close\n".encode())
            conn.sendall("Cache-Control: no-cache\n".encode())
            if start == None:
               start = len(data)-end
               end = len(data)-1
            if end == None:
               end = len(data)-1     
            conn.sendall(("Content-Type: " + self.fileType(filename) + "\n").encode())
            conn.sendall(("Content-Range: bytes "+str(start)+"-"+str(end)+"/"+str(len(data))+"\n").encode())
            conn.sendall(("Content-Length: "+str(end-start+1)+"\n\n").encode())
            conn.sendall(data[start:end+1]) 
            self.writelog("Partial transfer successful")                        
         file.close()         

   #Send the session state (state variables of all controls)
   def sendState(self, conn):
      conn.sendall("HTTP/1.1 200 OK\n".encode())
      conn.sendall("Content-Type: text/plain\n".encode())
      conn.sendall("Connection: close\n".encode())
      conn.sendall("\n".encode())
      self.writelog("Sending session state")
      for key in self.sessionState:
         if not key.startswith('$.record'):
            conn.sendall((key+'='+self.sessionState[key]+'\n').encode())
      for key in self.sessionHistory:
         conn.sendall(self.sessionHistory[key].encode());

   def fileType (self, filename):
       parts = filename.split('.')
       if (len(parts) > 1):
         extn = parts[1];
       else:
         extn = ""
       if extn == "png":
           filetype = "image/png"
       elif extn == "gif":
           filetype = "image/gif"
       elif extn == "jpeg":
           filetype = "image/jpeg"
       elif extn == "jpg":
           filetype = "image/jpeg"
       elif extn == "svg":
           filetype = "image/svg+xml"
       elif extn == "js":
           filetype = "application/javascript"
       elif extn == "htm" or extn == "html":
           filetype = "text/html"
       elif extn == "txt":
           filetype = "text/html"
       elif extn == "css":
           filetype = "text/css"
       elif extn == "mp4":
           filetype = "video/mp4"
       else:
           filetype = "application/octet-stream"
       return filetype

   def pollStatus (self) :
      data = ""

      self.keepaliveTimer.poll()
      self.statusTimeout.poll()
      
      data = VFP.pollStatus()

      # If the keepalive timer has expired we need to send a keep alive packet
      if len(data) == 0 and self.keepaliveTimer.isDue():
         self.writelog('Sending Keepalive');
         data = "$.keepalive\n"
         self.keepaliveTimer.reset()

      # If we have a status connection then use it to send the data,
      # otherwise we park it in a buffer unless the client has gone away.
      if len(data) != 0:
         if self.statusSocket != None:
            try:
              self.statusSocket.sendall(data.encode())
            except IOError:
              pass
            self.closeStatus()
         elif self.statusTimeout != None:
            self.statusBuffer += data
         else:
            self.statusBuffer = ""

      return

   # This is called when the client opens a reverse AJAX connection and we have nothing to send.
   def openStatus (self, sock):
      if self.statusSocket == None:
         # New Connection
         self.writelog("Client connected:"+str(sock.getpeername()[0]))
      if self.statusSocket != None:
         self.statusSocket.close()
      self.statusSocket = sock
      self.keepaliveTimer.start()
      self.statusTimeout.stop()

   # This is called to close status connection because we want the client to process the information
   # that we have written to it. At this point we start the a timeout timer, because we except to receive
   # another status connection within this time frame.
   def closeStatus (self):
      if self.statusSocket != None:
         self.statusSocket.close()
         self.statusSocket = None
      self.keepaliveTimer.stop()
      self.statusTimeout.reset()

   # This is triggered if/when the keepalive timer triggers.
   # It will cause the next call to pollStatus() to post a keepalive message and close the status pipe
   # at which point the server should request a new one.
   def keepaliveDue(self):
      pass

   # If the statusTimeout timer triggers then we can assume that we have lost contact with the client.
   def lostStatus(self):
      VFP.authorize(False)
      self.writelog("Client disconnected")
      self.clientAddress = None
      self.keepaliveTimer.stop()
      self.statusTimeout.stop()

   # Update the recorded state data.
   # Returns true is there is a state change which should be passed to the browser.
   def saveState(self, msg):
       m = re.match("([$a-zA-Z_][a-zA-Z0-9_\\.]*)\\s*=\\s*([^\\r\\n]*)", msg)
       dirty = False
       if m != None and len(m.groups()) == 2:
          # State assignment and history functions:
          key = m.group(1)
          value = m.group(2)
          if key.startswith("$.create"):
              dirty = True;
          elif key.startswith("$.record"):
              # Start recording for control with id=value
              id = value.replace('"', '')
              self.sessionState["$.record."+id] = "1"
          elif key.startswith("$.stop"):
              # Stop recording for control with id=value
              id = value.replace('"', '')
              self.sessionState["$.record."+id] = "0"
          elif key.startswith("$.erase"):
              # Erase recorded history for control with id=value
              id = value.replace('"', '')
              self.sessionHistory.pop(id, None)
          elif not key in self.sessionState or self.sessionState[key] != value:
              # Normal state assignment
              self.sessionState[key] = value
              dirty = True
       else:
          # Ordinary JS method call of form <id>.<method> (<args>)
          id = msg.split('.')[0]
          if self.sessionState.get("$.record."+id, '0') == '1':
             h = self.sessionHistory.get(id, '')+msg+'\n';
             self.sessionHistory[id] = h
          dirty = True;
       return dirty

   def writelog(self, msg):
       if os.path.exists(self.LOG_NAME):
          log = open(self.LOG_NAME, "a+")
          log.write(msg+'\n');
          log.close()
       #print(msg)

   def get_ip_address(self, ifname):
       s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       return socket.inet_ntoa(fcntl.ioctl(
           s.fileno(),
           0x8915,  # SIOCGIFADDR
           struct.pack('256s', ifname[:15])
       )[20:24])

   def configure (self, title):
      zeroconf.registerService(title, "_vfpserver._tcp", "local", self.PORT)

   def begin(self, port):
      # Set the PORT if specified on the command line:
      if port > 0:
         self.PORT  = port
            
      # Extract the project title from panel.svg
      # This should work using the XML library but the parser library is missing on the Yun Board.
      from html.parser import HTMLParser
      class SvgParser(HTMLParser):
         def __init__(self):
            HTMLParser.__init__(self)
            self.title = 'Virtual Front Panel'

         def handle_starttag(self, tag, attrs):
            if (tag == "svg"):
               for attr in attrs:
                  if attr[0] == 'vfp:title':
                     self.title = attr[1]

      # instantiate the parser and fed it some HTML
      try:
         parser = SvgParser()
         file = open(self.PANEL_SVG)
         parser.feed(file.read())
         file.close()
         self.applianceName = parser.title
         self.writelog("Configuring '"+parser.title+"'")
         
         #Perform configuration operations:
         self.configure(parser.title)
     
      except:
         self.writelog("Can't open "+self.PANEL_SVG)

      #Create, bind and listen on the socket:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.sock.bind((self.HOST, self.PORT))
      self.sock.listen(4)

      # Have we got wlan0:
      try:
         ipAddr = get_ip_address('wlan0')
         self.writelog("Listening on wlan0:"+ipAddr+":"+str(self.PORT))
      except:
         self.writelog("No IP for wlan0")

      # Have we got eth0:
      try:
         ipAddr = get_ip_address('eth0')
         self.writelog("Listening on eth0:"+ipAddr+":"+str(self.PORT))
      except:
         self.writelog("No IP for eth0")

      # Have we got eth1:
      try:
         ipAddr = get_ip_address('eth1')
         self.writelog("Listening on eth1:"+ipAddr+":"+str(self.PORT))
      except:
         self.writelog("No IP for eth1")
         
      serverThread = ServerThread()
      serverThread.server = self
      serverThread.start()
      
   def poll(self):
      pass

   def setTitle(self, title):
      VFP.setTitle(title)
   
   def debug(self, *args):
      if args:
         _delimiter = ","
         print(_delimiter.join(str(x) for x in args), "\n")

   def waitForRequests(self, delayms):
      time.sleep(delayms / 1000)
   
   def waitForTimeServer(self):
      #TBD
      pass
         
   def attachReloadHandler(self, handler):
      VFP.attachReloadHandler(handler)
      
   def attachLoginHandler(self, handler):
      VFP.attachLoginHandler(handler)
      
   def attachLogoutHandler(self, handler):
      VFP.attachLogoutHandler(handler)
      
   def attachRequestHandler(self, handler):
      VFP.attachRequestHandler(handler)
   
   
class ServerThread(threading.Thread):
   def run(self):
      while True:
         self.server.pollStatus()
         self.server.sock.setblocking(False);
         try:
            conn, addr = self.server.sock.accept()
            self.server.processRequest(conn, addr[0]);
         except socket.error:
            #No connection
            pass
