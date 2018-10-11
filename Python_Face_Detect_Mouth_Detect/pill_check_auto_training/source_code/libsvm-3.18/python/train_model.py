# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 11:10:58 2014

@author: dehua
"""
import os, subprocess
import random
import cv2
import shutil
from grid import *
from skimage.feature import hog
from svmutil import *
import svmutil
import svm


positive_data_folder = '/home/lei/test_data/takeda/My_collection/sample_positive'
negative_data_folder = '/home/lei/test_data/takeda/My_collection/sample_negitive'
label_pos = '1'
label_neg = '-1'
 

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
    
def normalizeImage(image):
    target_w = 64.0
    target_h = 64.0
    if image.shape[2] > 1:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)
    w = image.shape[1]
    h = image.shape[0]
    if (w < target_w) or (h < target_h) :
        if (w < ((h/2)+1)):
            image = cv2.resize(image,((int)(target_w), (int)((target_w/w)*h)))
        else:
            image = cv2.resize(image,((int)((target_h/h)*w), (int)(target_h)))  
    new_w = image.shape[1]
    new_h = image.shape[0]
 
    y_start = (int)(new_h/2 - target_h/2)
    x_start = (int)(new_w/2 - target_w/2)
    image = image[y_start:(y_start+target_h), x_start:(x_start+target_w)]
    
    return image

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
    for filename in imageSet: 
        if random.random()<percent:
            image = cv2.imread(filename)
            image = normalizeImage(image)
            hog_img(image, fileHandle, label)
    
def image_to_svm_feature(image):
    image = normalizeImage(image)
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    x = []
    for value in fd:
        x.append(value)
    return x
    
def imageSet2data(imageSet, label, percent, Y, X):
    
    for filename in imageSet: 
        if random.random()<percent:
            Y.append(label)
            image = cv2.imread(filename)
            feature =image_to_svm_feature(image)
            X.append(feature)
    return Y,X

def cleanfolder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    
def randomSelectData(input_folder, train_folder,test_folder, num_to_select):
    cleanfolder(train_folder)
    cleanfolder(test_folder)
    imageSet, total = walk(input_folder)
    
    testSet = []
    trainSet =random.sample(imageSet, num_to_select)
    
    for filename in imageSet:
        if filename not in trainSet:
            testSet.append(filename)
    
    train_sample = 0 
    test_sample =0
    for filename in trainSet:
        try:
            shutil.copy2(filename, train_folder+'/'+str(train_sample)+'.bmp')
        except IOError, e:
            print "Unable to copy file. %s" % e
        train_sample += 1
    for filename in testSet: 
        try:
            shutil.copy2(filename, test_folder+'/'+str(test_sample)+'.bmp')
        except IOError, e:
            print "Unable to copy file. %s" % e
        test_sample += 1
        
        
def createTestSet(train_folder, test_folder, num_train_data):
    randomSelectData(positive_data_folder, train_folder+'pos',test_folder+'pos', num_train_data) 
    randomSelectData(negative_data_folder, train_folder+'neg',test_folder+'neg', num_train_data)
    
def training(train_folder, percent, training_data_path, model_path):
    trainSet_pos, total = walk(train_folder+'pos')
    trainSet_neg, total = walk(train_folder+'neg')
    Y = []
    X = []    
    Y,X = imageSet2data(trainSet_pos,1,percent,Y,X)
    Y,X = imageSet2data(trainSet_neg,-1,percent,Y,X)
    traininFileHandle = open(training_data_path,'w')
    imageSet2Txtfile(trainSet_pos, label_pos, percent, traininFileHandle )
    imageSet2Txtfile(trainSet_neg, label_neg, percent, traininFileHandle )
    traininFileHandle.close()
    print 'find best parameters -c -g '
    rate, par = find_parameters(training_data_path)
    print 'training the model' 
    param = svm_parameter()
    param.C = par.get('c')
    param.gamma = par.get('g')
    prob = svm_problem(Y,X)
    m=svm_train(prob,param)
    svm_save_model(model_path,m)
    return m
    '''
    args = [svm_train_path,"-c",str(param.get('c')),"-g",str(param.get('g')),training_data_path,model_path]    
    print args    
    subprocess.call(args)
    '''
    
def testing(test_folder,  model_path):
    testSet_pos, total = walk(test_folder+'pos')
    testSet_neg, total = walk(test_folder+'neg')
    model = svm_load_model(model_path)
    Y = []
    X = [] 
    print 'predict positive  :'
    Y,X = imageSet2data(testSet_pos,1,1,Y,X)
    svm_predict(Y,X,model)
    print 'predict overall  :'
    Y,X = imageSet2data(testSet_neg,-1,1,Y,X)
    svm_predict(Y,X,model)
    
    
    '''
    label = 1
    total = 0 
    correct = 0
    for filename in testSet_pos:
        Y = []
        X = []
        image = cv2.imread(filename)
        feature = image_to_svm_feature(image)
        Y.append(label)
        X.append(feature)
        rlt = svm_predict(Y,X,model)
        total +=1
        if rlt[0][0] == label : 
            correct += 1
    print '=8=8=8=8=8=8=8=8=8=8=8=8=8='
    label=-1
    for filename in testSet_neg: 
        Y = []
        X = []
        image = cv2.imread(filename)
        feature = image_to_svm_feature(image)
        Y.append(label)
        X.append(feature)
        rlt = svm_predict(Y,X,model)
        total +=1
        if rlt[0][0] == label : 
            correct += 1
    print '(correct/total) ' + str(correct) + '/' + str(total)
    return correct, total
    '''



def runWholeProcess():
    
    
    ######################
    ######################
    
    train_data_folder6 = '/home/lei/test_data/takeda/test/test_set_14/train/'
    test_data_folder6 = '/home/lei/test_data/takeda/test/test_set_14/test/'
    model_folder6 = '/home/lei/test_data/takeda/test/test_set_14/model/'
    percents = [1.0]
    ######################
    
    train_data_folder = train_data_folder6
    test_data_folder =test_data_folder6
    model_folder = model_folder6
    num_of_training_data = 800
    
    print 'create image sets: '
    createTestSet(train_data_folder, test_data_folder, num_of_training_data)
    for percent in percents:
        model_path = model_folder+'model'+str(percent)+'.model'
        print model_path
        training(train_data_folder,percent, model_folder+'train'+str(percent), model_path )
        print 'self test ....'
        testing(train_data_folder, model_path)
        print 'other test ....'
        testing(test_data_folder, model_path)
        

runWholeProcess()
    
#testing('/home/lei/test_data/svm_random_test/tictac_test/test_set_5/test/',  '/home/lei/test_data/svm_random_test/tictac_test/test_set_5/model/model'+str(0.25)+'.model')
