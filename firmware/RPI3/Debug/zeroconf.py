import os

AVAHI_DAEMON = "/etc/init.d/avahi-daemon"
AVAHI_SERVICE  = "/etc/avahi/services/iotbuilder.service"
 
def registerService(title, type, domain, port):
   try:
      # Create the avahi-service descriptor file
      file = open(AVAHI_SERVICE,  "w")
      file.write("<?xml version='1.0' standalone='no'?>\n")
      file.write("<!DOCTYPE service-group SYSTEM 'avahi-service.dtd'>\n")
      file.write("<service-group>\n")
      file.write(" <name replace-wildcards='yes'>"+title+" on %h</name>\n")
      file.write(" <service>\n")
      file.write("   <type>"+type+"</type>\n")
      file.write("   <port>"+str(port)+"</port>\n") ## Could choose arbitrary/free port here
      file.write(" </service>\n")
      file.write("</service-group>\n")
      file.close();
      os.chmod(AVAHI_SERVICE, 0o644) # mark as non-executable
      # Publish the Service:
      os.system(AVAHI_DAEMON + " restart")
   except:
      pass

def deregisterService():
      os.remove(AVAHI_SERVICE) # remove configuration file
      # Unpublish the Service:
      os.system(AVAHI_DAEMON + " restart")
