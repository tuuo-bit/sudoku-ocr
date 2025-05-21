from server import VfpServer
import socket

# Control objects list
controls = []
status = ""
state = {}
reloadHandler = None
loginHandler = None
logoutHandler = None
requestHandler = None
history = {}
authorized = False

def toString(value):
   if isinstance(value, (bool)):
      if value:
         value = 1
      else:
         value = 0
   return str(value)

#Handlers
def callReloadHandlers():
   global controls
   global status
   global state

   #print("Reload")
   for control in controls:
      control.reloadHandler()
   for key in state.keys():
      status += str(key) + "=" + state[key] + "\n"
   for key in history.keys():
      status += history[key] + "\n"
   if reloadHandler != None:
      reloadHandler()
      
def callEventHandlers(event):
   global controls
   #print("Event: " + event)
   val = event.split(".")
   if len(val) == 1:
      val = event.split("=")
   for control in controls:
      if val[0] == control.getId():
         control.eventHandler(val[1])
   if requestHandler != None:
      requestHandler()

#Status
def pollStatus():
   global status
   _status = status
   #if status != "" : print("Status: " + status)
   status = ""
   return _status

def set(id, key, value):
   global status
   global state
   name = id + "." + key
   value = toString(value)
   if name in state.keys():
      if state[name] == value:
         return
   state[name] = value
   string = name + "=" + value + "\n"
   status += string

def call(object, method, *args):
   global status
   global history
   string = object + "." + method + "("
   if args:
      _delimiter = ","
      string += _delimiter.join(toString(x) for x in args)
   string += ")\n"
   status += string
   if object in history.keys():
      history[object] += string

def create(object, type):
   global status
   string = "$.create." + object + "=\"" + type + "\""
   status += string  + "\n"
   
def record(object, flag):
   global status
   global history
   if (flag):
      string = "$.start=" + object
      if not object in history.keys():
         history[object] = ""
   else:
      string = "$.stop=" + object
      del history[object]
   status += string  + "\n"
      
def erase(object):
   global status
   global history
   string = "$.erase=" + object
   status += string  + "\n"
   if object in history.keys():
      history[object] = ""
   
def setTitle(title):
   set("$", "title", title)
      
def debug(*args):
   if args:
      _delimiter = ","
      print(_delimiter.join(toString(x) for x in args))

def authorize(flag):
   global authorized
   global loginHandler
   global logoutHandler

   if (flag != authorized):
      print("Authorize: ", flag)
      authorized = flag

      if (flag and loginHandler != None):
         loginHandler()
      if (flag == False and logoutHandler != None):
         logoutHandler()

      set("$", "authorized", flag)

def isAuthorized():
   global authorized
   return authorized

def attachReloadHandler(handler):
   global reloadHandler
   reloadHandler = handler

def attachLoginHandler(handler):
   global loginHandler
   loginHandler = handler

def attachLogoutHandler(handler):
   global logoutHandler
   logoutHandler = handler

def attachRequestHandler(handler):
   global requestHandler
   requestHandler = handler