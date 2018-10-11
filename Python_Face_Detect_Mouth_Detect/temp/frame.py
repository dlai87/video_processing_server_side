import cv2
import os


video = "2017-01-09.flv"

if os.path.exists(video) == False : 
            self.errorOccur("input video file does not exist.")
        
videoPtr = cv2.VideoCapture(video)

count = 0 
while True:
	count += 1
	[result,img] = videoPtr.read()
	if not result:
		break
print count