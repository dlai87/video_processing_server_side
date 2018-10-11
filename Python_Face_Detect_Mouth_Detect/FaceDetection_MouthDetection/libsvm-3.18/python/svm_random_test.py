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
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
                total += 1
    return imageSet, total
    
def hog_img(image, fileHandle, label):
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    fileHandle.write(label)
    i = 0
    for value in fd:
        fileHandle.write(' '+str(i)+':'+str(value))
        i += 1
    fileHandle.write('\n')
    
def imageSet2Txtfile(imageSet, label, percent, fileHandle):
    resize_w = 32
    resize_h = 64
    for filename in imageSet: 
        if random.random()<percent:
            image = cv2.imread(filename)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
            image = cv2.resize(image,(resize_w, resize_h), interpolation = cv2.INTER_CUBIC)
            hog_img(image, fileHandle, label)

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
        
def createTestSet(train_folder, test_folder, num_train_data):
    randomSelectData(positive_data_folder, train_folder+'pos',test_folder+'pos', num_train_data) 
    randomSelectData(negative_data_folder, train_folder+'neg',test_folder+'neg', num_train_data)
    
def training(train_folder, percent, training_data_path, model_path):
    trainSet_pos, total = walk(train_folder+'pos')
    trainSet_neg, total = walk(train_folder+'neg')
    
    traininFileHandle = open(training_data_path,'w')
    imageSet2Txtfile(trainSet_pos, label_pos, percent, traininFileHandle )
    imageSet2Txtfile(trainSet_neg, label_neg, percent, traininFileHandle )
    traininFileHandle.close()
    print 'find best parameters -c -g '
    rate, param = find_parameters(training_data_path)
    print 'training the model'    
    args = [svm_train_path,"-c",str(param.get('c')),"-g",str(param.get('g')),training_data_path,model_path]    
    print args    
    subprocess.call(args)
    
def testing(test_folder, test_data_path, model_path):
    testSet_pos, total = walk(test_folder+'pos')
    testSet_neg, total = walk(test_folder+'neg')
    
    posTestDataFileHandle = open(test_data_path+'pos.txt','w')
    imageSet2Txtfile(testSet_pos, label_pos, 1, posTestDataFileHandle )
    posTestDataFileHandle.close()
    
    print 'predict the positive data...'
    args = svm_predict_path+' '+test_data_path+'pos.txt '+model_path +' output'   
    p = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    out1, err1 = p.communicate()
    
    negTestDataFileHandle = open(test_data_path+'neg.txt','w')
    imageSet2Txtfile(testSet_neg, label_neg, 1, negTestDataFileHandle )
    negTestDataFileHandle.close()
    
    print 'predict the negative data...'
    args = svm_predict_path+' '+test_data_path+'neg.txt '+model_path+' output'   
    p = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    out2, err2 = p.communicate()
    
    return out1, out2

def runWholeProcess():
    
    ######################
    
    train_data_folder1 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_1/train/'
    test_data_folder1 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_1/test/'
    model_folder1 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_1/model/'
    train_data_folder2 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_2/train/'
    test_data_folder2 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_2/test/'
    model_folder2 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_2/model/'
    train_data_folder3 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/train/'
    test_data_folder3 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/test/'
    model_folder3 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/model/'
    train_data_folder4 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_4/train/'
    test_data_folder4 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_4/test/'
    model_folder4 = '/home/lei/test_data/svm_random_test/tictac_test/test_set_4/model/'
    percents = [0.25,0.5,0.75,1.0]
    ######################
    
    train_data_folder = train_data_folder4
    test_data_folder =test_data_folder4
    model_folder = model_folder4
    num_of_training_data = 800
    
    log = open(model_folder+'log.txt','a')
    print 'create image sets: '
    createTestSet(train_data_folder, test_data_folder, num_of_training_data)
    for percent in percents:
        model = model_folder+'model'+str(percent)+'.model'
        training(train_data_folder,percent, model_folder+'train'+str(percent), model )
        print 'self test ....'
        pos_acc,neg_acc = testing(train_data_folder, model_folder+'self_test'+str(percent), model)
        print 'pos_acc ' + pos_acc + '\nneg_acc ' + neg_acc
        log.write('\n===self=== percent '+str(percent)+'\npos_acc'+pos_acc+'\nneg_acc ' + neg_acc)
        print 'other test ....'
        pos_acc,neg_acc = testing(test_data_folder, model_folder+'test'+str(percent), model)
        print 'pos_acc ' + pos_acc + '\nneg_acc ' + neg_acc
        log.write('\n ===other=== percent '+str(percent)+'\npos_acc'+pos_acc+'\nneg_acc ' + neg_acc)
    log.close()

runWholeProcess()
    

