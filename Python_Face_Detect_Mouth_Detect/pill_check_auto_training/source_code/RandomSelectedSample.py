# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 11:10:58 2014

@author: dehua
"""

import os, subprocess
import random
import shutil
import cv2
from grid import *
from skimage.feature import hog


positive_data_folder = '/home/lei/test_data/svm_random_test/tictac_test/SVM_TRAINING_DATA/Positive'
negative_data_folder = '/home/lei/test_data/svm_random_test/tictac_test/SVM_TRAINING_DATA/Negative'
label_pos = "1"
label_neg = "-1"
svm_train_path = '/home/lei/libsvm-3.18/svm-train'
svm_predict_path = '/home/lei/libsvm-3.18/svm-predict'    

def walk(path):
    imageSet = []
    total = 0 
    print path
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            print fileName
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
                total += 1
    return imageSet, total


def cleanfolder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    
def randomSelectData(input_folder, train_folder,test_folder, num_to_select):
    cleanfolder(train_folder)
    cleanfolder(test_folder)
    imageSet, total = walk(input_folder)
    chance = num_to_select*1.0/total
    trainSet = []
    testSet = []
    for filename in imageSet:
        if random.random()<chance:
            trainSet.append(filename)
        else:
            testSet.append(filename)
    for filename in trainSet:
    #    print filename
        shutil.copy2(filename, train_folder)
    for filename in testSet: 
    #    print filename
        shutil.copy2(filename, test_folder)
        

print 'start'
randomSelectData('/home/lei/Dropbox/dehua/Negative/','/home/lei/test_data/EB-1020/Data_Negative/neg_train/','/home/lei/test_data/EB-1020/Data_Negative/neg_test/', 10000)
print 'completed'
