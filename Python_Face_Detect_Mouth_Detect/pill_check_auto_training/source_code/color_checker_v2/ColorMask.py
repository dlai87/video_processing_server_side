# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 15:53:57 2014

@author: dehua
"""

import cv2
import numpy as np


low_ch1 = 0
low_ch2 = 0
low_ch3 = 0 
high_ch1 = 255
high_ch2 = 255
high_ch3 = 255


class ColorSupported:
    WHITE = 0
    GREEN = 1
    YELLOW = 2
    ORANGE =3
    BLUE = 4
    RED = 5
    CUSTOMIZED = 6
    SKIP = 999


class Singleton(object):  
    def __new__(cls, *args, **kw):  
        if not hasattr(cls, '_instance'):  
            orig = super(Singleton, cls)  
            cls._instance = orig.__new__(cls, *args, **kw)  
        return cls._instance  

# HLS color space
class ColorParameter(Singleton):
    def __init__(self):
        self.lowerScalar = np.array( [0,0,0],np.uint8)
        self.upperScalar = np.array([255,255,255],np.uint8)
    def setCustomizedParam(self, low1, low2, low3, high1, high2, high3):
        self.low_ch1 = low1
        self.low_ch2 = low2
        self.low_ch3 = low3
        self.high_ch1 = high1
        self.high_ch2 = high2
        self.high_ch3 = high3
    def getFixedLowerParam(self, color):
        if color ==  ColorSupported.WHITE:
            #self.lowerScalar = cv2.Scalar(25,0)
            pass
        elif color == ColorSupported.GREEN:
            self.lowerScalar = np.array([25,0, 140],np.uint8)
        elif color == ColorSupported.YELLOW:
            self.lowerScalar = np.array([75,60,140],np.uint8) 
        elif color == ColorSupported.ORANGE:
            self.lowerScalar = np.array([90,90,170],np.uint8)
        elif color == ColorSupported.BLUE:
            self.lowerScalar = np.array([0,45, 165],np.uint8)
        elif color == ColorSupported.RED:
            self.lowerScalar = np.array([110,25,90],np.uint8)
        elif color == ColorSupported.CUSTOMIZED:
            self.lowerScalar = np.array([low_ch1, low_ch2, low_ch3], np.uint8)
        return self.lowerScalar
    def getFixedUpperParam(self, color):
        if color ==  ColorSupported.WHITE:
            self.upperScalar = np.array([255,255,255],np.uint8)
        elif color == ColorSupported.GREEN:
            self.upperScalar = np.array([70,160,255],np.uint8)
        elif color == ColorSupported.YELLOW:
            self.upperScalar = np.array([100,200,255],np.uint8) 
        elif color == ColorSupported.ORANGE:
            self.upperScalar = np.array([115,220,255],np.uint8)
        elif color == ColorSupported.BLUE:
            self.upperScalar = np.array([25,150,255],np.uint8)
        elif color == ColorSupported.RED:
            self.upperScalar = np.array([150,150,255],np.uint8)
        elif color == ColorSupported.CUSTOMIZED:
            self.lowerScalar = np.array([high_ch1, high_ch2, high_ch3], np.uint8)
        return self.upperScalar
    def getDynamicLowerParam(self, inputImg, channel, topPercent ): 
        singleChannel = cv2.split(inputImg)[channel].reshape((1,-1))
        singleChannel.sort()
        index = (int)(singleChannel.shape[1]*(1-topPercent))
        self.lowerScalar = np.array([0,0,0])
        self.lowerScalar[channel] = singleChannel[0][index]
        return self.lowerScalar

        
class ColorMask(object):
    def __init__(self, mRgba):
        [self.RGB, self.HLS, self.RGB_WB, self.HLS_WB] = self.preprocess(mRgba)
        self.mask = mRgba.copy()
        self.w = mRgba.shape[1]
        self.h = mRgba.shape[0]
        self.lowerb = np.array([0,0,0],np.uint8)
        self.upperb = np.array([255,255,255],np.uint8)
    def preprocess(self, mRgba):
        RGB = mRgba.copy()
        RGB = cv2.GaussianBlur(RGB,(5,5),0)
        HLS = RGB.copy()
        HLS = cv2.cvtColor(RGB, cv2.COLOR_RGB2HLS, HLS)
        RGB_WB = self.whiteBalance(RGB)
        HLS_WB = self.whiteBalance(HLS)
        return [RGB,HLS,RGB_WB, HLS_WB]    
    def whiteBalance(self,img):
        img_temp = img.copy()
        [ch1,ch2,ch3]= cv2.split(img_temp)
        cv2.equalizeHist(ch1,ch1)
        cv2.equalizeHist(ch2,ch2)
        cv2.equalizeHist(ch3,ch3)
        img_temp = cv2.merge([ch1,ch2,ch3])
        return img_temp
    def getColorMask(self, color, enlargeScale = 0):
        colorParameter = ColorParameter()
        if color == ColorSupported.WHITE:
            self.lowerb = colorParameter.getDynamicLowerParam(self.HLS,1,0.18)
        else:
            self.lowerb = colorParameter.getFixedLowerParam(color)
        self.upperb = colorParameter.getFixedUpperParam(color)
        self.HLS = self.ShrinkPosition(self.HLS, enlargeScale)
        return self.getThresh(self.HLS)
        
    def getThresh(self,inputImg):
        self.mask = self.checkInRange(inputImg, self.lowerb, self.upperb)
        kernel = np.ones((4,4),np.uint8)
        self.mask = cv2.erode(self.mask,kernel,iterations = 1)
        self.mask = cv2.dilate(self.mask,kernel,iterations = 1)
        return self.mask
    def checkInRange(self,inputImg, lowerb, upperb):
        outputImg = inputImg.copy()
        for y in range(0,self.h-1):
            for x in range(0,self.w-1):
                if outputImg[y,x][0]>=lowerb[0] and outputImg[y,x][1]>=lowerb[1] and outputImg[y,x][2]>=lowerb[2] and outputImg[y,x][0]<=upperb[0] and outputImg[y,x][1]<=upperb[1] and outputImg[y,x][2]<=upperb[2]:
                    pass
                else:
                    outputImg[y,x][0] = 0 
                    outputImg[y,x][1] = 0 
                    outputImg[y,x][2] = 0 
        return outputImg
    def ShrinkPosition(self, inputImg, enlargeScale):
        w = (int)(self.w/(1+enlargeScale))
        h = (int)(self.h/(1+enlargeScale))
        x_start = (self.w -w)/2
        y_start = (self.h -h)/2
        #print "x_start " + str(x_start) + "w " + str(w) + "y_start " + str(y_start) + "h " + str(h) 
        return inputImg[y_start:(y_start + h-1),x_start:(x_start+w-1),:]
        
    


'''

if __name__ == "__main__":
    inputPath = "C:/Users/dehua/Desktop/images/pill_image_acc/white"
    outputPath = "C:/Users/dehua/Desktop/images/ColorCheckerV2/white/"
    
    for i in range(1, 301 ):
        
        imageName = inputPath + "(" + str(i) + ").jpg"
        print imageName
        img = cv2.imread(imageName)
        CM =ColorMask(img,[10,11,20,21])
        print outputPath+str(i)+"result.jpg"
        cv2.imwrite(outputPath+str(i)+"result.jpg", CM.getColorMask(ColorSupported.WHITE))
 #   lower = c.getFixedLowerParam(ColorSupported.GREEN)
 #   upper = c.getFixedUpperParam(ColorSupported.GREEN)
'''