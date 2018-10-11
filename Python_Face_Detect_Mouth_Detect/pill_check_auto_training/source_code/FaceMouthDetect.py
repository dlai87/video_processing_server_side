# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:36:25 2015

@author: dehua
"""


import cv2
import cv
import os
import Global



def drawCircle(img, point, color ):
    cv2.circle(img,point, 2, color, -1)

def drawCircleAroundRect(img, rect,color=(0,255,0)):
    """
    Draw 4 dots around the input rectangle
    """
    drawCircle(img, (rect[0],rect[1]),color)
    drawCircle(img, (rect[0]+rect[2],rect[1]), color)
    drawCircle(img, (rect[0],rect[1]+rect[3]), color)
    drawCircle(img, (rect[0]+rect[2],rect[1]+rect[3]), color)

def drawRect(img,rect,color = (0,255,0), lineWidth =1):
    x1 = rect[0]
    x2 = rect[0] + rect[2]
    y1 = rect[1]
    y2 = rect[1] + rect[3]
    cv2.rectangle(img, (x1, y1), (x2, y2), color, lineWidth)
        
def adjustROI(x,y,w,h,leftRatio, rightRatio, topRatio, botRatio):
    """
    Extend the region of interest.
    If negative value, it means that ROI is enlarged.
    Otherwise, ROI is reduced.
    """
    newX = x + (int)(leftRatio*w)
    newY = y + (int)(topRatio*h)
    newW = (int)(w * (float)(1-leftRatio-rightRatio))
    newH = (int)(h *(float)(1-topRatio-botRatio))
    return [newX,newY,newW,newH]

def checkRange(x,y,w,h,maxW,maxH):
    """
    Make sure x,y,w,h are valid values
    """
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + w >= maxW:
        w = maxW-x-1
    if y + h >= maxH:
        h = maxH-y-1
    return [x,y,w,h]
    
    
def adjustRoiWithinRange(x,y,w,h,leftRatio,rightRatio, topRatio,botRatio, maxW, maxH):
    [newX,newY,newW,newH] = adjustROI(x, y, w, h, leftRatio, rightRatio, topRatio, botRatio)
    [newX,newY,newW,newH] = checkRange(newX, newY, newW, newH, maxW, maxH)
    return  [newX,newY,newW,newH]

def smoothPos(inputRect, oldRect):
    """
    Smooth the detected rectangle to prevented from jumping around
    """
    ratio = oldRect[2] / inputRect[2]
    
    if abs(float(inputRect[0])-float(oldRect[0])) <15 and ratio > 0.99 and ratio < 1.01:
        return oldRect
    else:
        oldRect[0]=inputRect[0]
        oldRect[1]=inputRect[1]
        oldRect[2]=inputRect[2]
        oldRect[3]=inputRect[3]
        return oldRect

def getROI(inputImg,roi):
    [x,y,w,h] = roi
    return inputImg[(int)(y):(int)(y+h),(int)(x):(int)(x+w),:]
    


def areaComparator(A,B):
    (ax1,ay1,w1,h1) = A
    (bx1,by1,w2,h2) = B
    return w1*h1-w2*h2



class ObjDetector(object):
    def __init__(self,cascadeFilePath):
        assert os.path.exists(cascadeFilePath), "%s not exists"%cascadeFilePath
        self.detector = cv2.CascadeClassifier(cascadeFilePath)

    def detect(self,img,scale,minNeighbor,minSZ=(20,20),resizeWin=(-1,-1),flags = cv.CV_HAAR_SCALE_IMAGE):
        if resizeWin[0] >0 and resizeWin[1] >0:
            resizeImg = cv2.resize(img,resizeWin)
            cv2.imshow('subImg', resizeImg)
            temp = self.detector.detectMultiScale(resizeImg,scaleFactor=scale,minNeighbors=minNeighbor,minSize=minSZ,flags=flags)
            [h,w,channels] = img.shape
            xRatio = float(w)/resizeWin[0]
            yRatio = float(h)/resizeWin[1]
            for i in range(len(temp)):
                temp[i][0] = temp[i][0]*xRatio
                temp[i][1] = temp[i][1]*yRatio
                temp[i][2] = temp[i][2]*xRatio
                temp[i][3] = temp[i][3]*yRatio
        else:
            temp = self.detector.detectMultiScale(img,scaleFactor=scale,minNeighbors=minNeighbor,minSize=minSZ,flags=flags)

        if len(temp) == 0:
            return []
        else:
            return temp.tolist()

    def detect_biggest(self,img,scale,minNeighbor,minSZ=(20,20),resizeWin=(-1,-1),flags=cv.CV_HAAR_SCALE_IMAGE):
        rects = self.detect(img,scale,minNeighbor,minSZ,resizeWin,flags)
        if len(rects) == 0:
            return []
        else:
            rects.sort(areaComparator)
            return rects[-1]


class FaceMouthDetector:
    """
    This class detects face and mouth (if enabled) in an image. Draw the detected area if necessary
    """
    def __init__(self):
        self.faceXML = Global.current_path + "/faces_lbp_22.xml"
        self.mouthXML = Global.current_path + "/em_0514_lbp_51.xml"
        self.mouthScales = 1.2
        self.mouthNeighbors = 8
        self.faceScales = 1.1
        self.faceNeightbors = 3
        self.mouthDetector = ObjDetector(self.mouthXML)
        self.faceDetector = ObjDetector(self.faceXML)
        self.oldRect = None

    def getMouthPos(self, facePos):
        mouthPos = [0,0,0,0]
        mouthPos[0] = facePos[0]+facePos[2]/2-facePos[2]/6
        mouthPos[1] = facePos[1] + facePos[3]*3/4
        mouthPos[2] = facePos[2]/3
        mouthPos[3] = facePos[3]/4
        return mouthPos

    def process(self, img, enableMouthDetection = Global.DETECT_MOUTH_AREA_FLAG):
        """"
        This function detects face/mouth area if enabled. and draw if necessary
        It will return position if detected or [][] if not
        """
        mouthPos=[]
        [maxH,maxW,channels] = img.shape
        facePos = self.faceDetector.detect_biggest(img, self.faceScales, self.faceNeightbors)
       # print facePos
        if enableMouthDetection and len(facePos)>0:
            mouthDetectingArea = adjustRoiWithinRange(facePos[0], facePos[1], facePos[2], facePos[3], 0.1, 0.1, 0.5, -0.3, maxW, maxH)
            mouthRegionForDetection = getROI(img, mouthDetectingArea)
            mouthPos = self.mouthDetector.detect_biggest(mouthRegionForDetection, self.mouthScales, self.mouthNeighbors)
            if len(mouthPos) > 0:
                mouthPos[0] += mouthDetectingArea[0]
                mouthPos[1] += mouthDetectingArea[1]
        return [ facePos, mouthPos]
        
    def draw(self, img, facePos, mouthPos, enableMouthDetection = Global.DETECT_MOUTH_AREA_FLAG, draw = Global.DRAW_FACE_TRACKING):
        if len(facePos) > 0:
            if self.oldRect is None:
                self.oldRect = facePos
            newFacePos = smoothPos(facePos, self.oldRect)
            
            if draw:
                drawCircleAroundRect(img, newFacePos, (0,255,0))

            if enableMouthDetection:
                if len(mouthPos) > 0:
                    newMouthPos = mouthPos
                else:
                    newMouthPos = self.getMouthPos(newFacePos)
                if draw:
                    drawCircleAroundRect(img, newMouthPos, (255,0, 0))