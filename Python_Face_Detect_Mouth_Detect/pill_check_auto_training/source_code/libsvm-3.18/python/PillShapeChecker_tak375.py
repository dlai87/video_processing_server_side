"""
Created on Sat Apr 12 17:23:18 2014

@author: dehua
"""

from skimage.feature import hog
import cv2
import sys
import shutil
from svmutil import *


#negative_data_folder = '/home/lei/test_data/svm_random_test/tictac_test/SVM_TRAINING_DATA/Negative'


def walk(path):
    imageSet = []
    total = 0 
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1  ):
                imageSet.append(fileName)
                total += 1
    return imageSet
    
    
def image_to_svm_feature(image):
    image = normalizeImage(image)
    
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    x = []
    for value in fd:
        x.append(value)
    return x 

def CropCenterSquareImage(image):
    w = image.shape[1]
    h = image.shape[0]
    y_start = 0 
    target_h = 0 
    x_start = 0 
    target_w = 0
    if w < h :
        target_h = w
        target_w = w
        y_start = (int)(h/2-target_h/2)
    else :
        target_h = h
        target_w = h
        x_start = (int)(w/2-target_w/2)
    image = image[y_start:(y_start+target_h), x_start:(x_start+target_w)]
    return image

def normalizeImage(image):
    
    image = CropCenterSquareImage(image)
    target_w = 64.0
    target_h = 64.0
    if image.shape[2] > 1:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)
    w = image.shape[1]
    h = image.shape[0]
    if (w < target_w) or (h < target_h) :
       image = cv2.resize(image,((int)(target_w), (int)(target_h)))    
    return image
    
def predictOneImage(image):
    rlt = True 
    Y = []
    X = []
    feature = image_to_svm_feature(image)
    Y.append(1)
    X.append(feature)
    a = svm_predict(Y,X,model)
    if a[0][0] == -1.0 :
        rlt = False
    return rlt


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
    rlt = False
    checkFirstTime = predictOneImage(image)
    if checkFirstTime:
        rlt = True
        return rlt
    shrik_size = 0.95
    while shrik_size >= 0.6:   
        images = shrink(image, shrik_size)
        for img in images:
            checkSecondTime = predictOneImage(img)
            if checkSecondTime:
                rlt = True
                return rlt
        shrik_size -= 0.05
    return rlt
    

#img_path = '/home/lei/test_data/collect_data/log4.bmp'
#img_path = '/home/lei/test_data/svm_random_test/tictac_test/test_set_5/train/pos/435.bmp_0000_0116_0136_0057_0104.png'
model_path = '/home/lei/test_data/takeda/test/test_set_14/model/model1.0.model'
img_folder = '/home/lei/test_data/HOG_SVM/train_tictac'


saveImageInSeperateFolder = True
true_folder = '/home/lei/test_data/takeda/My_collection/True/t'
false_folder = '/home/lei/test_data/takeda/My_collection/False/f'

'''
img_path = str(sys.argv[1])
model_path = str(sys.argv[2])
'''

medication_type = 'tictac'
model = svm_load_model(model_path)

imageSet = walk(img_folder)

rlt_pos = 0
rlt_neg = 0 
for img_path in imageSet:
    image = cv2.imread(img_path)
    rlt = run(image) 
    if rlt:
        rlt_pos += 1
        print 'true'
        if saveImageInSeperateFolder:
            shutil.copy2(img_path, true_folder+str(rlt_pos)+'.bmp')
    else:
        rlt_neg += 1
        print 'false'
        if saveImageInSeperateFolder:
            shutil.copy2(img_path, false_folder+str(rlt_neg)+'.bmp')

print 'pos/neg: ' + str(rlt_pos)+'/'+str(rlt_neg)
