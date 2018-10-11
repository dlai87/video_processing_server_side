import cv2
import os
import sys
import numpy as np
import PillMask as pm
from color_checker_v2 import BlobDetector as bd
from color_checker_v2 import ColorMask as cm

from Util import *





hist = ColorHist()

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



def printColorToLog(img_original, img_grabcut):
    blobDetector = bd.BlobDetector(img_grabcut.shape[1], img_grabcut.shape[0])
    blobList = blobDetector.detectBlobs(img_grabcut, 50, -1, 50)
    if blobList:
        colorMask = cm.ColorMask(img_original)
        hist.addImage(colorMask.HLS_WB, img_grabcut)
        
        

def run(args):
    imageSet, total = walk(args.input_folder)
    for imagePath in imageSet:
        image = cv2.imread(imagePath)
        image = cv2.resize(image, (args.resize_w, args.resize_h), interpolation = cv2.INTER_CUBIC)
        grab = processOneImage(image)
        printColorToLog(image, grab)
        print "processed one image"
    hist.printHist(args.output, args.step_length)



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
    parser.add_argument("-o", "--output",
                        dest="output",
                        default="temp_output_color/hist",
                        help="output file")
    parser.add_argument("--resize_w",
                        dest="resize_w",
                        default=64,
                        type=int, 
                        help="resize image width")
    parser.add_argument("--resize_h",
                        dest="resize_h",
                        default=64,
                        type=int, 
                        help="resize image height")
    parser.add_argument("--step_length",
                        dest="step_length",
                        default=5,
                        type=int, 
                        help="increasement of step value in each channel")
    return parser    
        
        
if __name__ == "__main__":
    args = get_parser().parse_args()
    print "process start..."
    run(args)
    print "process completed..."