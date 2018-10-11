import FaceAligner as FA
import FeatureExtracter as FE
from sklearn.externals import joblib
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import Utility
import cv2
import os
import numpy as np
import logging
import time
from Util import *
import Util




class XGBClassifier:
    def __init__(self, modelFile, scalerFile, configFile="config.txt", threshold = 0.956255, numThreads=2):
        modelFile = absolutePathFile(modelFile)
        scalerFile =absolutePathFile(scalerFile)
        configFile = absolutePathFile(configFile)
        assert os.path.exists(modelFile), "%s does not exist" % modelFile
        assert os.path.exists(scalerFile), "%s does not exist" % scalerFile
        assert os.path.exists(configFile), "%s does not exist" % configFile
        self.scaler = joblib.load(scalerFile)
        self.classifier = xgb.Booster({'nthread': numThreads}) 
        self.classifier.load_model(modelFile)
        ConfigValue.Instance().load(configFile)

    def predict(self, fea1, fea2, needNormalize, threshold=0.956255):
    # For verifying if is the same person, suggested threshold = [0.271052, 0.0712623, 0.00853643]
    # For verifying two different people belong to the same person, suggested thresholds =[0.999639, 0.999934]
        feature = Utility.combineTwoFeatures(fea1, fea2)
        featureNormalized = self.scaler.transform(feature)
        dtest = xgb.DMatrix(featureNormalized)
        probability = self.classifier.predict(dtest) 
        label = probability > threshold
        return label, probability



class FaceRecognizer:
        
    def __init__(self, classifier, gpuMode=False, tplBaseName='0.tpl'): 
        self.faceAligner = FA.FaceAligner(shapeFile = absolutePathFile('target_shape.npy') )
        self.modelNames = ['0.25_0.25_0.5_0.58', '0.2_0.12_0.39_0.55', '0.2_0.12_0.3_0.38', '0.2_0.12_0.6_0.76', 'whole_face']
        self.allRatios = [[0.25, 0.25, 0.5, 0.58], [0.2, 0.12, 0.39, 0.55], [0.2, 0.12, 0.3, 0.38], [0.2, 0.12, 0.6, 0.76], [0.0, 0.0, 1.0, 1.0]]
        assert len(self.allRatios) == len(self.modelNames), "The number of models needs to match number of ratios"
        self.tplBaseName = tplBaseName
        self.classifier = classifier
        self.featureExtractors = []
        for i in xrange(len(self.modelNames)):
            self.featureExtractors.append(FE.FeatureExtracter(os.path.join('.', self.modelNames[i]), gpuMode=gpuMode))
    

    def extractFeature(self, img, ratios, featureExtractor):
        """
        img: input Imgage file
        ratios: [[x,y,w,h]]. Each image will be cropped based on the ratio.
        featureExtractor: need to match ratios. If there are 3 ratios, then there needs to be 3 feature extractors
        tmplFolderToSave: the directory to save the templates. Each feature extractor will have a sub directory in this.
        """
        xRatio = ratios[0]
        yRatio = ratios[1]
        widthRatio = ratios[2]
        heightRatio = ratios[3]
        if xRatio == 0.0 and yRatio == 0.0 and widthRatio == 1.0 and heightRatio == 1.0:
            roiImg = img
        else:
            roiImg = Utility.getRoiUsingWidthAndHeight(img, xRatio, yRatio, heightRatio, widthRatio)
        imgName = "%s_%s_%s_%s.jpg" % (xRatio, yRatio, widthRatio, heightRatio);
        #print "============save img roi=================="
        #cv2.imwrite(imgName, roiImg)
        templTmpl = featureExtractor.extractTemplate(roiImg)
        return templTmpl

    def extractTemplate(self, inputImg, detectFace):
        """
        img1: 3 channels image. Make sure it is in Ndarray format. The image needs to be in the format BGR (compatible with OPENCV), and its scale needs to be [0,255]
        templateName: if none. Then do not save template. If not none, save the template in a desired position
        return: the template used for matching or saving
        """
        if detectFace:
            alignedImg = self.faceAligner.transformImg(inputImg)
            if alignedImg is None:
                return None
            # cv2.imwrite('face_aligned.jpg', alignedImg)
        else:
            alignedImg = inputImg
        tpls = []
        for i in xrange(len(self.allRatios)):
            ratio = self.allRatios[i]
            featureExtractor = self.featureExtractors[i]
            tpl = self.extractFeature(alignedImg, ratio, featureExtractor)
            tpls.append(tpl)
        return tpls
        
    def saveTemplates(self, tpls, tplBaseFolder):
        modelNames = self.modelNames
        for tpl, modelName in zip(tpls, modelNames):
            tplFolder = os.path.join(tplBaseFolder, modelName)
            if os.path.exists(tplFolder) is False:
                os.makedirs(tplFolder)
            tplName = os.path.join(tplFolder, self.tplBaseName)
            #if os.path.exists(tplName):
                # logging.warning("%s already exists. Will be overwritten" % tplName)
            tpl.dump(tplName)

    def readTemplates(self, tplBaseFolder):
        """
        tplFolder: the folder where to save the template
        if read failed, return None
        """
        modelNames = self.modelNames
        finalTemplate = None
    
        for model in modelNames:
            tplName = os.path.join(tplBaseFolder, model, self.tplBaseName)
            if not os.path.exists(tplName):
                # logging.error("%s does not exist" % tplName)
                return None
            else:
                tpl = np.load(tplName) 
                if finalTemplate is None:
                    finalTemplate = tpl 
                else:
                    finalTemplate = np.hstack((tpl, finalTemplate))
        return finalTemplate

    def match(self, tp1, tp2, threshold=0.956255, needNormalize=True):
    # For verifying if is the same person, suggested threshold = [0.271052, 0.0712623, 0.00853643]
    # For verifying two different people belong to the same person, suggested thresholds =[0.999639, 0.999934]
        label, probability = self.classifier.predict(tp1, tp2, needNormalize, threshold=threshold)
        return label, probability