# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 15:08:25 2014

@author: dehua
"""

import os
import cv2


def walk(path):
    imageSet = []
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            print fileName
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1 ):
                if(fileName.find(".xvpics") == -1):                
                    imageSet.append(fileName)
            if(fileName.find(".gif") != -1  or fileName.find(".pgm") != -1):
                img = cv2.imread(fileName)
                cv2.imwrite(fileName+".jpg", img)
                imageSet.append(fileName+".jpg")
    return imageSet
    
def getFileList(input_folder, output_file):
    files = walk(input_folder)
    output_file_handle = open(output_file,'w')
    total = 0 
    for filename in files:
        output_file_handle.write(filename)
        output_file_handle.write('\n')
        total += 1
    output_file_handle.close()
    print 'total serch images: '+str(total)

def cropImage(file_list, output_folder):
    f = open(file_list)
    lines = f.readlines()
    index = 0 
    for line in lines:
        element = line.split()
        img = cv2.imread(element[0])
        if img is not None: 
            x = int(element[1])
            y = int(element[2])
            w = int(element[3])
            h = int(element[4])
            sub = img[y:(y+h), x:(x+w)]
            cv2.imwrite(output_folder+str(index)+'.bmp', sub)
            index += 1
    f.close()
    print 'total crop images: '+str(index)
    
    
def flipImage(image_path):
    images = walk(image_path)
    total = 0 
    for filename in images:
        img = cv2.imread(filename)
        img = cv2.flip(img,1)
        cv2.imwrite(image_path+"/flip/r"+str(total)+".jpg", img)
        total+=1
    

def rotateImage(input_image_path, output_image_path):
    images = walk(input_image_path)
    total = 0 
    for filename in images:
        print 'filename ' + filename
        img = cv2.imread(filename)
        if img is not None: 
            img = img.copy()
            img = cv2.transpose(img,img)
            img = cv2.flip(img,-1)
            cv2.imwrite(output_image_path +str(total)+".bmp", img)
            total+=1

def runWholeProcess():
    
    ######################
    image_path = '/home/lei/test_data/takeda/My_collection/level_1_4_neg'
    exec_file_path = '/home/lei/test_data/HOG_SVM/detector/detect_samples_save_coordinate_main'
    
    '''
    detector_xml_file_path = '/home/lei/test_data/takeda/tak375large_12_26_92.xml'
    file_list_path = '/home/lei/test_data/takeda/generic_file_list.txt'
    scale = '1.2'
    numNeighbor = '4'
    winWidth = '12'
    winHeight = '26'
    '''
    detector_xml_file_path = '/home/lei/test_data/takeda/tak375pillsonly_12_12_36.xml'
    file_list_path = '/home/lei/test_data/takeda/generic_file_list.txt'
    scale = '1.3'
    numNeighbor = '7'
    winWidth = '12'
    winHeight = '12'
    
    show = '0'
    resultFile = '/home/lei/test_data/takeda/resultFile.txt'
    saveCropImageFolderAndFilenamePrefix = '/home/lei/test_data/takeda/My_collection/level_2_4/level_2_4_detector'
   
    ######################   
    print '=== generate file list ==='
    getFileList(image_path,file_list_path)
    print '=== find false positive list ==='
    arg1 = ' -inputFileList ' + file_list_path
    arg2 = ' -xml ' + detector_xml_file_path
    arg3 = ' -scale ' + scale
    arg4 = ' -numNeighbor ' + numNeighbor
    arg5 = ' -winWidth ' + winWidth
    arg6 = ' -winHeight ' + winHeight
    arg7 = ' -show ' + show
    arg8 = ' -resultFile ' + resultFile
    command = exec_file_path + arg1 + arg2 + arg3 + arg4 + arg5 + arg6 + arg7 + arg8
    print command
    os.system(command )
    
    print '=== crop image ==='
    cropImage(resultFile,saveCropImageFolderAndFilenamePrefix)
    print '=== completed ==='
    
    
runWholeProcess() 
#flipImage('/home/lei/test_data/takeda/Positive/whole_screen')
#rotateImage('/home/lei/test_data/takeda/My_collection/image', '/home/lei/test_data/takeda/My_collection/my_rotated/fullscreen_')
