# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 15:57:51 2015

@author: dehua lai
"""


from skimage.feature import hog
import cv2
import sys
import subprocess
import Global
import xml.etree.ElementTree as ET
sys.path.insert(0, './libsvm-3.18/python')

from svmutil import *


def hog_img_memory(image, label):
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    x = {}
    i = 0
    for value in fd:
        x[int(i)] = float(value) 
        i += 1
    return int(label), x

def image_to_svm_feature_memory(image):
    y = []
    x = []
    label, value = hog_img_memory(image,1)
    y.append(label)
    x.append(value)
    return y, x



def preProcess(image):
    medication_type_exist = False
    if Global.medication_type == "Tictac":
        image, medication_type_exist = customize_model_base_on_type(image,'/model/TICTAC.0.0-200.model', 32,64)
    
    # TAK is no longer use
    #if Global.medication_type == "TAK-375SL":
    #    image, medication_type_exist = customize_model_base_on_type(image,'/model/TAK-375SL.model', 64,64)
    
    if Global.medication_type == "CTN":
        image, medication_type_exist = customize_model_base_on_type(image,'/model/CTN-1.0-400.model', 64,64)
        
    # if the medication type is not pre-defined, treat as tictac
    if medication_type_exist==False:
        image, medication_type_exist = customize_model_base_on_type(image,'/model/TICTAC.0.0-200.model', 32,64)
    
    model = svm_load_model(Global.MODEL_FILE)
    return image, model
    

def customize_model_base_on_type(image, modelName, target_w, target_h):
    Global.MODEL_FILE = Global.current_path + modelName
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
    image = cv2.resize(image,(target_w, target_h), interpolation = cv2.INTER_CUBIC)
    image = chopImage(image,target_w, target_h)
    cv2.imwrite('./hello.jpg', image)
    return image, True

def chopImage(image,w,h):
    height, width = image.shape
    if width <= height:
        image = cv2.resize(image,(w, w*height/width), interpolation = cv2.INTER_CUBIC)
        new_h, new_w = image.shape
        image = image[(new_h-h)/2:(new_h-h)/2+h, 0:new_w ]
    else:
        image = cv2.resize(image,(h*width/height, h), interpolation = cv2.INTER_CUBIC)
        new_h, new_w = image.shape
        image = image[0:new_h, (new_w-w)/2:(new_w-w)/2+w ]
    return image
    
def svmPredict(image):
    image, model = preProcess(image)
    y, x = image_to_svm_feature_memory(image)
    p_labs, p_acc, p_vals = svm_predict(y, x, model , '-b 1' )

    score = [] 
    for vals in p_vals:
        if vals[1] != 0:
            s = vals[0]/vals[1]
        else:
            s = 999999
        score.append(s)
    return score


def predictOneImage(image, thresh):
    score = svmPredict(image)
#    print score
    if score[0] > thresh:
        return True
    else:
        return False 


def shrink(image, shrink_size):
    w = image.shape[1]
    h = image.shape[0]
    shrink_w =(int)( w*shrink_size)
    shrink_h =(int)( h*shrink_size)
    x = [0 , (w-shrink_w)/2, (w-shrink_w)]
    y = [0 , (h-shrink_h)/2, (h-shrink_h)]
    imagelist = []
    for i in range(0,3):
        for j in range(0,3):
            img = image[y[i]:(y[i] + shrink_h), x[j]:(x[j]+ shrink_w)]
            imagelist.append(img)
    return imagelist

def run(image):
#    global medication_type 
#    medication_type = medicationType
#    global feature_file_path
#    feature_file_path = featureFile
    param = ET.parse('pill_detect_parameter.xml').getroot()    
    confidence_threshold = float(param.attrib.get('confidence_threshold'))

    index = 0
    rlt = False
    checkFirstTime = predictOneImage(image, confidence_threshold)
    if checkFirstTime:
        rlt = True
        return rlt
    # Since we lower the threshold of confidence level, there is no need to iterate check and shrink images
    '''
    shrik_size = 0.9
    while shrik_size >= 0.7: 
        images = shrink(image, shrik_size)
        for img in images:
            index +=1
            checkSecondTime = predictOneImage(img, confidence_threshold)
            if checkSecondTime:
                rlt = True
                return rlt
        shrik_size -= 0.1
    return rlt
    '''

'''
#image = cv2.imread('./25010.bmp_0000_0138_0105_0026_0052.png') 
image = cv2.imread('./face1.bmp') 
rlt = run(image)
print rlt
'''

    