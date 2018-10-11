# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 15:51:31 2014

@author: dehua
"""

import cv2



class Blob(object):
    def __init__(self, xMin, xMax, yMin, yMax, mass):
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.mass = mass
    def __str__(self):
        return "X: %4d -> %4d, Y: %4d -> %4d, mass: %6d" %(self.xMin,self.xMax,self.yMin,self.yMax,self.mass )
    def __lt__(self, other):
         return self.mass < other.mass
        
    

class BlobDetector(object): 
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.labelBuffer = [0]*width*height
        tablesize = width*height/4
        self.labelTable = [0]*tablesize
        self.xMinTable = [0]*tablesize
        self.xMaxTable = [0]*tablesize
        self.yMinTable = [0]*tablesize
        self.yMaxTable = [0]*tablesize
        self.massTable = [0]*tablesize
    def detectBlobs(self ,srcData, minBlobMass, maxBlobMass, background ):
        srcPtr = 0 
        aPtr = -self.width - 1
        bPtr = -self.width
        cPtr = -self.width + 1
        dPtr = -1
        label = 1
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.labelBuffer[srcPtr] = 0 
                if (srcData[y,x][0] > background):
                    aLabel = self.labelTable[self.labelBuffer[aPtr]] if (x > 0 and y > 0)  else 0
                    bLabel = self.labelTable[self.labelBuffer[bPtr]]  if y > 0 else 0
                    cLabel = self.labelTable[self.labelBuffer[cPtr]] if (x < self.width-1 and y > 0) else 0
                    dLabel = self.labelTable[self.labelBuffer[dPtr]] if x > 0 else 0 
                    min_temp = 999999
                    if (aLabel != 0 and aLabel < min_temp): 
                        min_temp = aLabel
                    if (bLabel != 0 and bLabel < min_temp): 
                        min_temp = bLabel
                    if (cLabel != 0 and cLabel < min_temp): 
                        min_temp = cLabel;
                    if (dLabel != 0 and dLabel < min_temp): 
                        min_temp = dLabel;
                        
                    if (min_temp == 999999):
                        self.labelBuffer[srcPtr] = label;
                        self.labelTable[label] = label;
                        self.yMinTable[label] = y;
                        self.yMaxTable[label] = y;
                        self.xMinTable[label] = x;
                        self.xMaxTable[label] = x;
                        self.massTable[label] = 1;
                        label += 1;
                    else:
                         self.labelBuffer[srcPtr] = min_temp;
                         self.yMaxTable[min_temp] = y;
                         self.massTable[min_temp] += 1;
                         if (x < self.xMinTable[min_temp]):
                             self.xMinTable[min_temp] = x;
                         if (x > self.xMaxTable[min_temp]):
                             self.xMaxTable[min_temp] = x;
                         if (aLabel != 0):
                             self.labelTable[aLabel] = min_temp;
                         if (bLabel != 0):
                             self.labelTable[bLabel] = min_temp;
                         if (cLabel != 0):
                             self.labelTable[cLabel] = min_temp;
                         if (dLabel != 0):
                             self.labelTable[dLabel] = min_temp;
                srcPtr += 1
                aPtr += 1
                bPtr += 1
                cPtr += 1
                dPtr += 1
                                
                
        blobList = []
        for i in range(label-1, 0, -1):
            if(self.labelTable[i] != i):
                if(self.xMaxTable[i] > self.xMaxTable[self.labelTable[i]]):
                    self.xMaxTable[self.labelTable[i]] = self.xMaxTable[i]
                if (self.xMinTable[i] < self.xMinTable[self.labelTable[i]]):
                    self.xMinTable[self.labelTable[i]] = self.xMinTable[i]
                if (self.yMaxTable[i] > self.yMaxTable[self.labelTable[i]]):
                    self.yMaxTable[self.labelTable[i]] = self.yMaxTable[i]
                if (self.yMinTable[i] < self.yMinTable[self.labelTable[i]]):
                    self.yMinTable[self.labelTable[i]] = self.yMinTable[i]
                self.massTable[self.labelTable[i]] += self.massTable[i];
                l = i 
                while l != self.labelTable[l]:
                    l = self.labelTable[l]
                self.labelTable[i] = l
            else:
                if (self.massTable[i] >= minBlobMass & (self.massTable[i] <= maxBlobMass or maxBlobMass == -1)):
                    blob = Blob(self.xMinTable[i], self.xMaxTable[i], self.yMinTable[i], self.yMaxTable[i], self.massTable[i])
                    blobList.append(blob)
        blobList.sort(reverse=True)
        return blobList
                             
'''       
if __name__ == "__main__":
    inputPath = "C:/Users/dehua/Desktop/images/test/fusion/2fusion_img.jpg"
    img = cv2.imread(inputPath)
    (img, cv2.COLOR_BGR2GRAY, img)
    blobDetector = BlobDetector(img.shape[1], img.shape[0])
    blobList = blobDetector.detectBlobs(img, 50, -1, 50)
    print blobList[0]
'''
                     