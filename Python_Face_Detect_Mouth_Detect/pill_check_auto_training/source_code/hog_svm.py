# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 16:21:54 2014

@author: dehua
"""

import os, subprocess
import cv2
from grid import *

from skimage.feature import hog


def walk(path):
    imageSet = []
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
    return imageSet
    
def hog_img(image, fileHandle, label):
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    fileHandle.write(label)
    i = 0
    for value in fd:
        fileHandle.write(' '+str(i)+':'+str(value))
        i += 1
    fileHandle.write('\n')
    
  #  hog_image = hog_image*255
  #  return hog_image
    

def run_whole_process():
    ######################
    training_sample_path_pos = '/home/lei/test_data/HOG_SVM/test/true_tictac'
    training_sample_path_neg = '/home/lei/test_data/HOG_SVM/test/false_positive_tictac'
    testing_sample_path_pos = '/home/lei/test_data/HOG_SVM/old_data/tic/pill_in_hand/pill_in_hand_nih_2/b'
    testing_sample_path_neg = '/home/lei/test_data/HOG_SVM/old_data/suboxone/high'
    svm_train_path = '/home/lei/libsvm-3.18/svm-train'
    svm_predict_path = '/home/lei/libsvm-3.18/svm-predict'    
    model_path = '/home/lei/test_data/HOG_SVM/model_tic_sub'
    output_path = '/home/lei/test_data/HOG_SVM/output_tic_sub.txt'
    label_pos = '1'
    label_neg = '-1'
    training_data_path = '/home/lei/test_data/HOG_SVM/train_tic_sub'
    testing_data_path = '/home/lei/test_data/HOG_SVM/test_tic_sub'   
    resize_w = 64
    resize_h = 128
    ######################   
    
    print "loading training image and generate data ... "
    images_pos = walk(training_sample_path_pos)
    images_neg = walk(training_sample_path_neg)
    
    trainingDataFileHandle = open(training_data_path,'w')

    for filename in images_pos: 
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, trainingDataFileHandle, label_pos)
    for filename in images_neg:
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, trainingDataFileHandle, label_neg)
    
    trainingDataFileHandle.close()
    
    print 'find best parameters -c -g '
    rate, param = find_parameters(training_data_path)
    
    print 'training the model'    
    args = [svm_train_path,"-c",str(param.get('c')),"-g",str(param.get('g')),training_data_path,model_path]    
    print args    
    subprocess.call(args)
    
    
    print "loading testing image and generate data ... "
    
    images_pos = walk(testing_sample_path_pos)
    images_neg = walk(testing_sample_path_neg)
    
    testingDataFileHandle = open(testing_data_path,'w')

    for filename in images_pos: 
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, testingDataFileHandle, label_pos)
        '''
    for filename in images_neg:
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, testingDataFileHandle, label_neg)
    '''
    
    testingDataFileHandle.close()
    
    print 'predict the testing data...'
    args = [svm_predict_path,testing_data_path,model_path,output_path]  
    print args 
    subprocess.call(args)
    
def validation():
    ######################
  #  testing_sample_path_pos = '/home/lei/test_data/HOG_SVM/old_data/tic/pill_in_hand/pill_in_hand_nih_1/b'
    testing_sample_path_pos ='/home/lei/test_data/HOG_SVM/train_tictac'    
    testing_sample_path_neg = '/home/lei/test_data/HOG_SVM/old_data/suboxone/squaredd'
    svm_predict_path = '/home/lei/libsvm-3.18/svm-predict'    
    model_path = '/home/lei/test_data/HOG_SVM/model_tic_sub'
    output_path = '/home/lei/test_data/HOG_SVM/output_tic.txt'
    label_pos = '1'
    label_neg = '-1'
    testing_pos_path = '/home/lei/test_data/HOG_SVM/test_pos' 
    testing_neg_path = '/home/lei/test_data/HOG_SVM/test_neg'
    resize_w = 64
    resize_h = 128
    ######################   
    print "loading testing pos image and generate data ... "
    
    images_pos = walk(testing_sample_path_pos)
    posDataFileHandle = open(testing_pos_path,'w')
    for filename in images_pos: 
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, posDataFileHandle, label_pos)
    posDataFileHandle.close()
    print 'predict the positive data...'
    args = [svm_predict_path,testing_pos_path,model_path,output_path]   
    subprocess.call(args)
    
    print "loading testing neg image and generate data ... "
    images_neg = walk(testing_sample_path_neg)
    negDataFileHandle = open(testing_neg_path,'w')
    for filename in images_neg:
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
        hog_img(image, negDataFileHandle, label_neg)
    negDataFileHandle.close()
    print 'predict the negative data...'
    args = [svm_predict_path,testing_neg_path,model_path,output_path]   
    subprocess.call(args)
    
#run_whole_process()
validation()