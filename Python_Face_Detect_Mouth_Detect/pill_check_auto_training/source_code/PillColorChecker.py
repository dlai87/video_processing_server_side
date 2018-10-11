# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 16:34:01 2014

@author: dehua
"""

import PillMask as pm
from color_checker_v2 import BlobDetector as bd
from color_checker_v2 import ColorMask as cm
import cv2
import numpy as np
import Global




def processOneImage(image):
    width = image.shape[1]
    height = image.shape[0]
    x = (int)(0.18*width)
    y = (int)(0.18*height)
    w = (int)(0.8*width)
    h = (int)(0.8*height)
    rect = (x,y,w,h); 
    ColorSpaceSequences = ['RGB','YUV','LAB','LUV','YCrCb']
    tempImage = []
    for colorCode in ColorSpaceSequences: 
        preProImg = pm.preProcess(image,colorCode)
        grabCutImg = pm.grabCut(preProImg, rect)
        tempImage.append(grabCutImg)
    [img_fusion, maxValue] = pm.fusion(tempImage,width,height)
    img_crop = pm.fusionImageDisplay(image, img_fusion, maxValue, width, height)
    return img_crop
    

def determineColor(img_original, img_grabcut, color):
    blobDetector = bd.BlobDetector(img_grabcut.shape[1], img_grabcut.shape[0])
    blobList = blobDetector.detectBlobs(img_grabcut, 50, -1, 50)
    if blobList:
        if color == cm.ColorSupported.WHITE or color == cm.ColorSupported.YELLOW:
            colorMask = cm.ColorMask(img_original)
            yellow = colorMask.getColorMask(cm.ColorSupported.YELLOW)
            white = colorMask.getColorMask(cm.ColorSupported.WHITE)
            isWhite = judge(img_grabcut,white)
            isYellow = judge(img_grabcut,yellow)
            if isWhite ==1:
                return True
        if color == cm.ColorSupported.RED: 
            colorMask = cm.ColorMask(img_original)
            red = colorMask.getColorMask(cm.ColorSupported.RED)
            isRed = judge(img_grabcut,red)
            if isRed == 1: 
                return True
    return False

"""
def determineColorWhite(img_original, img_grabcut):
    blobDetector = bd.BlobDetector(img_grabcut.shape[1], img_grabcut.shape[0])
    blobList = blobDetector.detectBlobs(img_grabcut, 50, -1, 50)
    if blobList:
        colorMask = cm.ColorMask(img_original)
        yellow = colorMask.getColorMask(cm.ColorSupported.YELLOW)
        white = colorMask.getColorMask(cm.ColorSupported.WHITE)
        isWhite = judge(img_grabcut,white)
        isYellow = judge(img_grabcut,yellow)
        if isWhite ==1:
            return True
      #  if isWhite == 1 and isYellow == 0:
      #      return True
    return False
"""



def determineColor_CustomizedColor(img_original, img_grabcut, low1, low2, low3, high1, high2, high3):
    blobDetector = bd.BlobDetector(img_grabcut.shape[1], img_grabcut.shape[0])
    blobList = blobDetector.detectBlobs(img_grabcut, 50, -1, 50)
    if blobList:
        colorMask = cm.ColorMask(img_original)
        colorMask.setCustomizedParam(low1, low2, low3, high1, high2, high3)
        mask = colorMask.getColorMask(cm.ColorSupported.CUSTOMIZED)
        score = judge(img_grabcut, mask)
        return score > 0
    return False



def judge(img_grabcut, img_mask):
    status = 0; 
    width = img_mask.shape[1]
    height = img_mask.shape[0]
    gray1 = cv2.cvtColor(img_grabcut, cv2.COLOR_BGR2GRAY, img_grabcut)
    gray2 = cv2.cvtColor(img_mask, cv2.COLOR_BGR2GRAY, img_mask)
    for y in range(0,height):
        for x in range(0, width):
            if (gray1[y,x] > 0) and (gray2[y,x] > 0):
                img_mask[y,x] = np.array([255,255,255],np.uint8)
            else:
                img_mask[y,x] = np.array([0,0,0],np.uint8)
    blobDetector = bd.BlobDetector(img_mask.shape[1], img_mask.shape[0])
    blobList = blobDetector.detectBlobs(img_mask, 50, -1, 50)
    if blobList:
        #print 'color detected : ======================= '
        #print blobList[0]
        ratio = blobList[0].mass*1.0 / (width*height)
        if ratio > Global.PILL_COLOR_WHITE_RATIO_TREASH:
            status = 1
        #print 'ratio: ' + str(ratio)
        #cv2.imwrite(output_folder+str(index)+'wwww'+str(ratio)+'.bmp', img_mask)
    return status

def run(image):
    medication_type_exist = False
    color = cm.ColorSupported.WHITE
    if Global.medication_type.lower() == "tictac":
        image = cv2.resize(image,(32, 64), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
    if Global.medication_type.lower() == "ctn":
        image = cv2.resize(image,(64, 64), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
    # la county white
    if Global.medication_type.lower() == "isoniazid" or Global.medication_type.lower() == "pyridoxine":
        image = cv2.resize(image,(48, 64), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
    # la county pink
    if Global.medication_type.lower() == "rifapentine":
        image = cv2.resize(image,(64, 64), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
        color = cm.ColorSupported.SKIP
    # la county red
    if Global.medication_type.lower() == "rifampin":
        image = cv2.resize(image,(40, 120), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
        color = cm.ColorSupported.RED
    # sf truvada blue
    if Global.medication_type.lower() == "truvada":
        image = cv2.resize(image,(64, 48), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
        color = cm.ColorSupported.BLUE
    # pfizer white capsule
    if Global.medication_type.lower() == "pf-04958242":
        image = cv2.resize(image,(48, 96), interpolation = cv2.INTER_CUBIC)
        medication_type_exist = True
    
    if color == cm.ColorSupported.SKIP:
        return True
        
    if medication_type_exist == False:
        image = cv2.resize(image,(64, 64), interpolation = cv2.INTER_CUBIC)
    grab = processOneImage(image)
    return determineColor(image,grab, color)


