# -*- coding: utf-8 -*-
"""
Created on Tue May 12 19:03:35 2015

@author: lei
"""


import Global
import cv2
import os
import sys
import time
from joblib import Parallel, delayed

from FaceMouthDetect import ObjDetector


NUM_THREAD = 1

def walk(path):
    imageSet = []
    total = 0 
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
                total += 1
    return imageSet, total
    
    
def getROI(inputImg,roi):
    [x,y,w,h] = roi
    return inputImg[(int)(y):(int)(y+h),(int)(x):(int)(x+w),:]
    
    
class PillDetector:
    """
    This class detects face and mouth (if enabled) in an image. Draw the detected area if necessary
    """
    def __init__(self):
        """
        # CTN
        self.pillDetector1 = Global.current_path + "/detector_xml/white_round_tablet_29.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/white_round_tablet_flat_30.xml"
        self.pillScales1 = 1.05
        self.pillNeightbors1 = 4
        self.pillScales2 = 1.05
        self.pillNeightbors2 = 5
        """
        """
        #truvada
        self.pillDetector1 = Global.current_path + "/detector_xml/truvada_blue_tablet_pid_h_18_12_lbp_34.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/truvada_blue_tablet_pid_v_10_18_lbp_30.xml"
        self.pillScales1 = 1.2
        self.pillNeightbors1 = 5
        self.pillScales2 = 1.4
        self.pillNeightbors2 = 6
        """
        """
        #la_county_white
        self.pillDetector1 = Global.current_path + "/detector_xml/white_tablet_horizontal_big_small_18_14_lbp_32.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/white_tablet_round_big_small_12_18_lbp_31.xml"
        self.pillScales1 = 1.05
        self.pillNeightbors1 = 5
        self.pillScales2 = 1.05
        self.pillNeightbors2 = 2
        """
        """
        #la_county_pink
        self.pillDetector1 = Global.current_path + "/detector_xml/pink_tablet_round_12_14_lbp_33.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/pink_tablet_round_12_14_lbp_33.xml"
        self.pillScales1 = 1.05
        self.pillNeightbors1 = 2
        self.pillScales2 = 1.05
        self.pillNeightbors2 = 2

        """
        """
        #la_county_red_orange
        self.pillDetector1 = Global.current_path + "/detector_xml/orange_red_capsule_pih_24_12_36.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/orange_red_capsule_pill_in_hand_8_24_lbp_35.xml"
        self.pillScales1 = 1.1
        self.pillNeightbors1 = 6
        self.pillScales2 = 1.2
        self.pillNeightbors2 = 4
        """

        #white_capsule
        self.pillDetector1 = Global.current_path + "/detector_xml/white_capsule_size1_pid_h_16_10_lbp_31.xml"
        self.pillDetector2 = Global.current_path + "/detector_xml/white_capsule_size1_pid_v_12_20_lbp_40.xml"
        self.pillScales1 = 1.1
        self.pillNeightbors1 = 5
        self.pillScales2 = 1.1
        self.pillNeightbors2 = 6
        
        self.pillDetector1 = ObjDetector(self.pillDetector1)
        self.pillDetector2 = ObjDetector(self.pillDetector2)
        self.oldRect = None
        
    def process(self, img, saveFolder, saveName):
        
        [maxH,maxW,channels] = img.shape
        pillPos1 = self.pillDetector1.detect_biggest(img, self.pillScales1, self.pillNeightbors1)
        pillPos2 = self.pillDetector2.detect_biggest(img, self.pillScales2, self.pillNeightbors2)
        if len(pillPos1) > 0 :
            cv2.imwrite(saveFolder+"/"+saveName+"_1.jpg", getROI(img, pillPos1))
        if len(pillPos2) > 0 :
            cv2.imwrite(saveFolder+"/"+saveName+"_2.jpg", getROI(img, pillPos2))
        
def batchImageDetection(args):
    imageSet, total = walk(args.input_folder)
    if NUM_THREAD == 1:
        processImageSet(args, "Thread-1", imageSet)
    else : 
        images = []
        numThread = NUM_THREAD
        for i in range (numThread):
            images.append(imageSet[i*len(imageSet)/numThread:(i+1)*len(imageSet)/numThread])
        try:
            Parallel(n_jobs=numThread, backend="threading")(delayed(processImageSet)(args,"-Thread-"+str(i)+"-", images[i] ) for i in range(numThread))
        except Exception, e:
            print "Error: unable to start thread, Exception: " + str(e)
    
def chopImage(image,w,h):
    height = image.shape[0]
    width = image.shape[1]
    if width <= height:
        image = cv2.resize(image,(w, w*height/width), interpolation = cv2.INTER_CUBIC)
    else:
        image = cv2.resize(image,(h*width/height, h), interpolation = cv2.INTER_CUBIC)
    return image

           
def processImageSet(args, threadName, imageSet):
    print threadName
    detector = PillDetector()
    index = 0 
    for imageName in imageSet:
        try:
            image = cv2.imread(imageName)
            if args.need_resize:
                image = chopImage(image, 480,640)
            saveNames = imageName.split("/")
            saveName = saveNames[len(saveNames)-1]
            saveName += threadName
            saveName += "-"+str(index)+"-"
            print 'processing ' + saveName 
            detector.process(image, args.output_folder, saveName)
            index +=1
        except:
            print sys.exc_info()
            
        
def is_valid_file(parser, arg):
    """Check if arg is a valid file that already exists on the file
       system.
    """
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg
        
def get_parser():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_folder",
                        dest="input_folder",
                        type=lambda x: is_valid_file(parser, x),
                        help="folder of images to be detected")
    parser.add_argument("-o", "--output_folder",
                        dest="output_folder",
                        type=lambda x: is_valid_file(parser, x),
                        help="folder where detected image should be saved")
    parser.add_argument("--need_resize",
                        dest="need_resize",
                        type=int,
                        default=1,
                        help="whether the images need to be resized? 0 == no need; 1 needed ")
    
    
    return parser    
        
if __name__ == "__main__":
    args = get_parser().parse_args()
    print "processing...."
    batchImageDetection(args)
    print "main thread exit...."