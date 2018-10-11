import svmutil
import svm
from svmutil import *
import cv2
from skimage.feature import hog


def walk(path):
    imageSet = []
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
    return imageSet
    
    
def image_to_svm_feature(image):
    resize_w = 32
    resize_h = 64
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)
    image = cv2.resize(image,(resize_w, resize_h))
    fd = hog(image, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(1, 1), visualise=False)
    x = []
    for value in fd:
        x.append(value)
    return x
    
    
svm_model.predict = lambda self, x: svm_predict([0], [x], self)[0][0]
prob = svm_problem([1,1,-1], [[1,1,1], [-1,0,-1],[10,10,10]])
param = svm_parameter()
param.kernel_type = LINEAR
param.C = 10
m=svm_train(prob)

def train():
    pos_path = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/train/pos'
    neg_path = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/train/neg'
    y = []
    x = []
    pos_image = walk(pos_path)
    neg_image = walk(neg_path)
    print 'train pos'
    for filename in pos_image:
        y.append(1)
        image = cv2.imread(filename)
        feature = image_to_svm_feature(image)
        x.append(feature)
    print 'train pos'
    for filename in neg_image:
        y.append(-1)
        image = cv2.imread(filename)
        feature = image_to_svm_feature(image)
        x.append(feature)
    print 'train -----'
    prob = svm_problem(y,x)
    print 'train ====='
    mdl = svm_train(prob)
    return mdl
        
    

x = m.predict([10,10,10])
print x
model_path = '/home/lei/test_data/svm_random_test/tictac_test/test_set_3/model/model0.8'
model = svm_load_model('/home/lei/save.model')
#model = train()
#svm_save_model('/home/lei/save.model',model)


imageset = walk('/home/lei/test_data/svm_random_test/tictac_test/test_set_3/test/pos')
for filename in imageset: 
    image = cv2.imread(filename)
    feature = image_to_svm_feature(image)
    xx= model.predict(feature)
    print '=========='
    print xx

