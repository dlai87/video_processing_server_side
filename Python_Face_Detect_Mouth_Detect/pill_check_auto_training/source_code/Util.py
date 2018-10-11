# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:25:37 2015

@author: dehua
"""
import cv2
import os
import sys
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt


class ColorHist:
    def __init__(self):
        self.H = []
        self.L = []
        self.S = []
    def addImage(self, img_hls, img_grabcut):
        [ch1,ch2,ch3]= cv2.split(img_hls)
        for i in range(0,img_hls.shape[0]):
            for j in range(0,img_hls.shape[1]):
                if img_grabcut[i,j][0] !=0 or img_grabcut[i,j][1]!=0 or img_grabcut[i,j][2]!=0 :
                    self.H.append(ch1[i,j])
                    self.L.append(ch2[i,j])
                    self.S.append(ch3[i,j])

    def getOneChannel(self, channel, step_length):
        total = len(channel)
        hist_dict = OrderedDict()
        if total <=0 : 
            return hist_dict
        i = 0 
        while i < 255:
            counter = 0
            for value in channel:
                if value >= i and value < i+step_length:
                    counter +=1
            title = str(i) + '-'+str(i+step_length)
            if i+step_length > 255:
            	title = str(i) + '-255'
            hist_dict[title] = counter*100.0/total
            i += step_length
            if i> 255 and i-255 < step_length:
                i = 255
        return hist_dict
    def printFormat(self, dic, save_file, channel_name):
        plt.bar(range(len(dic)), dic.values(), align='center')
        plt.xticks(range(len(dic)), dic.keys(), rotation=25)
        plt.savefig(str(save_file)+'_'+str(channel_name)+'.png')
        

    def printHist(self, save_file='hist', step_length=5, channel=3):
        if channel == 0:
            channel1 = self.getOneChannel(self.H, step_length)
            self.printFormat(channel1, save_file, "Hue") 
        elif channel == 1:
            channel2 = self.getOneChannel(self.L, step_length)
            self.printFormat(channel2, save_file, "Ligtness") 
        elif channel == 2:
            channel3 = self.getOneChannel(self.S, step_length)
            self.printFormat(channel3, save_file, "Saturation") 
        else:
            channel1 = self.getOneChannel(self.H, step_length)
            self.printFormat(channel1, save_file, "Hue") 
            channel2 = self.getOneChannel(self.L, step_length)
            self.printFormat(channel2, save_file, "Ligtness") 
            channel3 = self.getOneChannel(self.S, step_length)
            self.printFormat(channel3, save_file, "Saturation") 