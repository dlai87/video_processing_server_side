# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 14:57:20 2016

@author: dehua
"""

import os
import sys
import cv2
import numpy as np



class Frame(object):
    def __init__(self, image, frameID, videoID):
        self.image = image
        self.frameID = frameID
        self.videoID = videoID

    def printInfo(self, message):
        print message + ": vid " + str(self.videoID) + " fid " + str(self.frameID)


class Controller(object):
    
    def __init__(self):
        pass

    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    def mse(self, imageA, imageB):
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err
        
    # private method
    def countFrames(self, video):
        if os.path.exists(video) == False : 
            self.errorOccur("input video file does not exist.")
        videoPtr = cv2.VideoCapture(video)
        videoFrameID = 0
        
        while True:
            [result,img] = videoPtr.read()
            if not result:
                break
            videoFrameID += 1
        return videoFrameID

    def loadVideoToImageArray(self, video, videoID = 0):
        if os.path.exists(video) == False : 
            self.errorOccur("input video file does not exist.")
        videoPtr = cv2.VideoCapture(video)
        videoFrameID = 0
        frames = []
        while True:
            [result,img] = videoPtr.read()
            if not result:
                break
            frame = Frame(img, videoFrameID, videoID)
            videoFrameID += 1
            frames.append(frame)
        return frames

    def findMissingFrame(self, subVideos, mergeVideo):
        subVideoFrames = []
        mergeVideoFrames = []
        index = 0 
        for subV in subVideos:
            subVideoFrames.extend(self.loadVideoToImageArray(subV, index))
            index += 1

        mergeVideoFrames.extend(self.loadVideoToImageArray(mergeVideo))
        frameTotalSubVideo = len(subVideoFrames)
        frameTotalMergeVideo = len(mergeVideoFrames)

        print "Total num frames of sub videos : " + str(frameTotalSubVideo)
        print "Total num frames of merge video : " + str(frameTotalMergeVideo)

        missingFrameFound = False
        for i in range(0, frameTotalMergeVideo):
            frame1 = mergeVideoFrames[i]
            frame2 = subVideoFrames[i]
            err = self.mse(frame1.image, frame2.image)
            if err > 0 :
                print err
                print frame1.printInfo("merge")
                print frame2.printInfo("sub")
                missingFrameFound = True

        if missingFrameFound:
            print "Missing Frame Found"
        else :
            print "Missing Frame are last 3 frames"



       
        
if __name__ == '__main__':
    print "start"
    controller = Controller()
    print "=========== test case 1 =========="
    subVideos = ["NAME=newSUFFIX=0.mp4","NAME=newSUFFIX=1.mp4","NAME=newSUFFIX=2.mp4","NAME=newSUFFIX=3.mp4","NAME=newSUFFIX=4.mp4"]
    mergeVideo = "new.mp4"
    controller.findMissingFrame(subVideos, mergeVideo)
    print "=========== test case 2 =========="
    subVideos = ["NAME=TTSUFFIX=0.mp4","NAME=TTSUFFIX=1.mp4"]
    mergeVideo = "TT.mp4"
    controller.findMissingFrame(subVideos, mergeVideo)
    print "=========== test case 3 =========="
    subVideos = ["NAME=case3SUFFIX=0.mp4","NAME=case3SUFFIX=1.mp4","NAME=case3SUFFIX=2.mp4","NAME=case3SUFFIX=3.mp4"]
    mergeVideo = "case3.mp4"
    controller.findMissingFrame(subVideos, mergeVideo)
    print "=========== test case 4 =========="
    subVideos = ["NAME=case4SUFFIX=0.mp4","NAME=case4SUFFIX=1.mp4","NAME=case4SUFFIX=2.mp4"]
    mergeVideo = "case4.mp4"
    controller.findMissingFrame(subVideos, mergeVideo)
    
   
    print "complete"