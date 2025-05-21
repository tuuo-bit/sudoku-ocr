import os
import picamera

class RPiCamera:
   
   def __init__ (self):
      self.camera = picamera.PiCamera()
      self.filestem = 'image'
      self.camera.resolution = (640, 480)
      self.count = 0

   def setFilestem (self, fs):
      self.filestem = fs
      self.count = 0
      
   def setResolution(self, w, h):
      self.camera.resolution = (w,h)               

   def reset(self):
      self.count=0
      
   def capture(self, q):
      self.camera.capture(self.getImage(self.count), quality=q)
      self.count = self.count + 1;

   def getImage(self,  count):
      return self.filestem+format(count, '05d')+'.jpg'

   def getLastImage(self):
      if self.count > 0:
         return self.getImage(self.count-1)
      return ""   
      
   def getImageCount(self):
      return self.count
      
   def makeVideo(self, framerate):
      if self.count > 0:
         cmd = "ffmpeg -start_number 0 -framerate "+str(framerate)+" -i "+self.filestem+"%05d.jpg"+" -vframes "+str(self.count)+"  -vcodec libx264 -pix_fmt yuv420p -threads 1 " + self.filestem+".mp4 -y"
         if ("ffmpeg" in dir(self.camera)):
            self.camera.ffmpeg(cmd)
         else:
            os.system(cmd)         

   def startRecording(self, filename):
      base = os.path.splitext(filename)[0]
      self.filename = filename
      self.rawfile = base+".h264"
      self.camera.start_recording(self.rawfile)

   def stopRecording(self):
      self.camera.stop_recording()
      cmd="ffmpeg -i "+self.rawfile+" -pix_fmt yuv420p "+self.filename
      if ("ffmpeg" in dir(camera)):
         self.camera.ffmpeg(cmd)
      else:  
         os.system(cmd)         
      os.remove(self.rawfile)
