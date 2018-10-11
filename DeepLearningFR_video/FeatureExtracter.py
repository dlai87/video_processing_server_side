import os
import cv2
import caffe
import numpy
import logging
import time
from Util import *

class FeatureExtracter:
    def __init__(self, modelFolder, templateBaseName="0.tpl", featureLayer='fc0_0', networkFile ='feature.prototxt',  gpuMode=False):
        """
        modelFolder should have 3 files: feature.prototxt, mean.binaryproto, deploy.caffemodel
        """
        if gpuMode:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()
        model = os.path.join( absolutePathFile(modelFolder), 'deploy.caffemodel')
        meanFile = os.path.join(absolutePathFile(modelFolder), 'mean.npy')
        prototxtFeature = os.path.join(absolutePathFile(modelFolder), networkFile)
        assert os.path.exists(model)
        assert os.path.exists(meanFile)
        assert os.path.exists(prototxtFeature)
        self.netFeature = caffe.Net(prototxtFeature, model, caffe.TEST)
        self.transformer = caffe.io.Transformer({'data': self.netFeature.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2, 0, 1))
        self.transformer.set_mean('data', numpy.load(meanFile))
        self.transformer.set_input_scale('data', 1 / 255.0)
        # self.transformer.set_channel_swap('data', (2, 1, 0))
        self.netFeature.blobs['data'].reshape(1, 3, 64, 64)
        self.featureLayer = featureLayer
        self.tplBaseName = templateBaseName

    def extractTemplate(self, img):
        """
        img1: 3 channels image. Make sure it is in Ndarray format. The image needs to be in the format BGR (compatible with OPENCV), and its scale needs to be [0,255]
        templateName: if none. Then do not save template. If not none, save the template in a desired position
        return: the template used for matching or saving
        """
        # print "TODO: need to take care of mean data"
        # img1 = img / 255.0
        self.netFeature.blobs['data'].data[...] = self.transformer.preprocess('data', img)
        out = self.netFeature.forward()
        return numpy.copy(out[self.featureLayer])

    def saveTemplate(self, tpl, tplFolder):
        if not os.path.exists(tplFolder):
            os.makedirs(tplFolder)
        tplName = os.path.join(tplFolder, self.tplBaseName)
        # if os.path.exists(tplName):
        #     logging.warning("%s already exists. Will be overwritten" % tplName)
        tpl.dump(tplName)

    """
    tplFolder: the folder where to save the template
    if read failed, return None
    """
    def readTemplate(self, tplFolder):
        tplName = os.path.join(tplFolder, self.tplBaseName)
        if not os.path.exists(tplName):
            # logging.error("%s does not exist" % tplName)
            return None
        else:
            tpl = numpy.load(tplName)
            return numpy.copy(tpl)


if __name__ == '__main__':

    fe = FeatureExtracter('whole_face')
    img = cv2.imread('gaoyuanyuan1.jpg')
    tmpl = fe.extractTemplate(img)
    print tmpl

    featureExtractorToSave = FeatureExtracter('whole_face', featureLayer='conv2_1', networkFile ='feature_collection_layer.prototxt')
    tmpl1 = featureExtractorToSave.extractTemplate(img)
    print tmpl1   