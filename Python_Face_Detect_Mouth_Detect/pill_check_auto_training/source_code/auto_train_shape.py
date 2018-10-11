# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 11:10:58 2014

@author: dehua
"""

import os, subprocess
import sys
import random
import shutil
import cv2
from skimage.feature import hog
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
import numpy as np
from grid import *
import sys

sys.path.insert(0, 'libsvm-3.18/python')

from svmutil import *


INPUT_LABEL_TRAIN_POS = "#train_pos#"
INPUT_LABEL_TRAIN_NEG = "#train_neg#"
INPUT_LABEL_TEST_POS = "#test_pos#"
INPUT_LABEL_TEST_NEG = "#test_neg#"


label_pos = "1"
label_neg = "-1"




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

def hog_img_memory(image, label):
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    x = {}
    i = 0
    for value in fd:
        x[int(i)] = float(value) 
        i += 1
    return int(label), x
    

def cleanfolder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    

def fileToPath(args):
    train_pos = []
    train_neg = []
    test_pos = []
    test_neg = []
    with open(args.input_file) as f:
        for line in f:
            if INPUT_LABEL_TRAIN_POS in line:
                train_pos.append(line.replace(INPUT_LABEL_TRAIN_POS,'').replace('\n',''))
            if INPUT_LABEL_TRAIN_NEG in line:
                train_neg.append(line.replace(INPUT_LABEL_TRAIN_NEG,'').replace('\n',''))
            if INPUT_LABEL_TEST_POS in line:
                test_pos.append(line.replace(INPUT_LABEL_TEST_POS,'').replace('\n',''))
            if INPUT_LABEL_TEST_NEG in line:
                test_neg.append(line.replace(INPUT_LABEL_TEST_NEG,'').replace('\n',''))
    return train_pos, train_neg, test_pos, test_neg
    

def train(args, set_pos, set_neg):
    trainSet_pos = []
    for path in set_pos:
        tempSet, total = walk(path)
        trainSet_pos = np.append(trainSet_pos, tempSet)
    trainSet_neg = []
    for path in set_neg:
        tempSet, total = walk(path)
        trainSet_neg = np.append(trainSet_neg, tempSet)
    
    train_txt_file = args.out_folder+'/train.txt'
    model_file = args.out_folder+'/'+args.model
    
    traininFileHandle = open(train_txt_file,'w')
    imageSet2Txtfile(trainSet_pos, label_pos, traininFileHandle , args, True)
    imageSet2Txtfile(trainSet_neg, label_neg, traininFileHandle , args, True)
    traininFileHandle.close()
    print 'find best parameters -c -g '
    rate, param = find_parameters(train_txt_file)
    print 'training the model'    
    svm_args = [args.svm_train,"-b", "1",  "-c",str(param.get('c')),"-g",str(param.get('g')),train_txt_file, model_file]    
    print svm_args    
    subprocess.call(svm_args)
    
def test(args, set_pos, set_neg):
    testSet_pos = []
    for path in set_pos:
        tempSet, total = walk(path)
        testSet_pos = np.append(testSet_pos, tempSet)
    testSet_neg = []
    for path in set_neg:
        tempSet, total = walk(path)
        testSet_neg = np.append(testSet_neg, tempSet)
    
    test_pos_file = args.out_folder+'/test-pos.txt'
    model_file = args.out_folder + '/' + args.model
    output = args.out_folder+'/output'
    
    model = svm_load_model(model_file)

    labels = []
    scores = []

    print 'predict positive data:'
    
    label, score = predict(testSet_pos, test_pos_file, label_pos, model, args)
    for i in range(len(label)):
        labels.append(label[i])
        scores.append(score[i])
    
    test_neg_file = args.out_folder+'/test-neg.txt'
    
    print 'predict negative data:'
    label, score = predict(testSet_neg, test_neg_file, label_neg, model, args)
    for i in range(len(label)):
        labels.append(label[i])
        scores.append(score[i])

 #   plot_roc(labels, scores, args)



def plot_roc(labels, scores, args):
    fpr, tpr, thresholds = roc_curve(labels, scores)
    outFile = open( args.out_folder + '/plot_roc-output'+str(args.n)+'.txt','w')
    for i in range(len(fpr)):
        outFile.write(str(fpr[i, ]) + ' '+str(tpr[i,]) + ' '+ str(thresholds[i,] )+ '\n' )
    outFile.close()
    fpr.dump(args.out_folder + '/plot_roc-fpr_new')
    tpr.dump(args.out_folder +'/plot_roc-tpr_new')
    thresholds.dump(args.out_folder +'/plot_roc-thresholds_new')
    plt.plot(fpr, tpr)
    plt.savefig(args.out_folder +'/'+args.med_label+'.png')

    
def predict(testSet,test_file, label, model, args):
    y, x = imageSet2Memory(testSet, label, args)
    p_labs, p_acc, p_vals = svm_predict(y, x, model , '-b 1' )
    
    score = [] 
    for vals in p_vals:
        if vals[1] != 0:
            s = vals[0]/vals[1]
        else:
            s = 999999
        score.append(s)

    return y, score
    
    """
    testDataFileHandle = open(test_file,'w')
    imageSet2Txtfile(testSet, label, testDataFileHandle , args)
    testDataFileHandle.close()
    svm_args = args.svm_predict + ' -b 1 ' + test_file +' ' +  model_file +' '+output  
    print svm_args
    p = subprocess.Popen(svm_args, stdout=subprocess.PIPE,shell=True)
    out, err = p.communicate()
    print out
    print err 
    """   
    
def imageSet2Memory(imageSet, label, args):
    y = []
    x = []
    for filename in imageSet:
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(args.resize_w, args.resize_h), interpolation = cv2.INTER_CUBIC)
        image = chopImage(image,args.resize_w, args.resize_h)
        label, value = hog_img_memory(image,label)
        y.append(label)
        x.append(value)
    return y , x

def imageSet2Txtfile(imageSet, label, fileHandle, args, limitImages = False):
    if limitImages:
        imageSet = random.sample(imageSet, args.n)
    index = 0
    for filename in imageSet: 
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
        image = cv2.resize(image,(args.resize_w, args.resize_h), interpolation = cv2.INTER_CUBIC)
        image = chopImage(image,args.resize_w, args.resize_h)
        index +=1
        hog_img(image, fileHandle, label)


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
    parser.add_argument("-i", "--input_file",
                        dest="input_file",
                        type=lambda x: is_valid_file(parser, x),
                        help="txt file contains input folder information")
    """
    parser.add_argument("-trp", "--train_pos",
                        dest="train_pos",
                        type=lambda x: is_valid_file(parser, x),
                        help="positive data folder for training")
    parser.add_argument("-trn", "--train_neg",
                        dest="train_neg",
                        type=lambda x: is_valid_file(parser, x),
                        help="negative data folder for training")
    parser.add_argument("-tep", "--test_pos",
                        dest="test_pos",
                        type=lambda x: is_valid_file(parser, x),
                        help="positive data folder for testing")
    parser.add_argument("-ten", "--test_neg",
                        dest="test_neg",
                        type=lambda x: is_valid_file(parser, x),
                        help="negative data folder for testing")
    """
    parser.add_argument("-out_folder", 
                        dest="out_folder",
                        type=lambda x: is_valid_file(parser, x),
                        default='temp_output_shape/',
                        help="the folder where to store output model and other output files")
    parser.add_argument("-model", 
                        dest="model",
                        default="default.model",
                        help="the folder where to store output model and other output files")
    parser.add_argument("-resize_img_w",
                        dest="resize_w",
                        default=32,
                        type=int,
                        help="resize image width before extract features, default 32")
    parser.add_argument("-resize_img_h",
                        dest="resize_h",
                        default=64,
                        type=int,
                        help="resize image height before extract features, default 64")
    parser.add_argument("-svm_train", 
                        dest="svm_train",
                        default='libsvm-3.18/svm-train',
                        type=lambda x: is_valid_file(parser, x),
                        help="svm training program")
    parser.add_argument("-svm_predict_path", 
                        dest="svm_predict",
                        default='libsvm-3.18/svm-predict',
                        type=lambda x: is_valid_file(parser, x),
                        help="svm predict program")
    parser.add_argument("-n",
                        dest="n",
                        default=600,
                        type=int,
                        help="how many data will be trained")
    parser.add_argument("-med_label",
                        dest="med_label",
                        default="med_color_shape_type",
                        help="description of medicaiton features such as name, color, shape, type")
    parser.add_argument("-log",
                        dest="log",
                        default="message.log",
                        help="log file for all screen outputs")
    
    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()
    train_pos, train_neg, test_pos, test_neg = fileToPath(args)
    print '====================='
    print train_pos
    print train_neg
    print test_pos
    print test_neg
    print '====================='
   # old_stdout = sys.stdout
   # log_file = open(args.log,"w")
   # sys.stdout = log_file


    train(args, train_pos, train_neg)
    test(args, test_pos, test_neg)
    
   # sys.stdout = old_stdout
   # log_file.close()
    