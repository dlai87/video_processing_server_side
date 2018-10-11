# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 14:57:20 2016

@author: dehua
"""

import os
import sys
import cv2
from Util import *
from FaceRecognizer import *
from Model import *



MAX_NUM_SAVE_TPL = 50
EXTRACT_FACE_FRAME_SKIP = 4
EXTRACT_FACE_STEP_ID = 0




class Controller(object):
    
    def __init__(self):
        classifier = XGBClassifier('xgboost.model',  scalerFile='xgboost.scaler')
        self.faceRecognizer = FaceRecognizer(classifier, gpuMode = False)
        FinalResult.Instance().initDefaultValue()
        
    
    def loadInputJson(self, input_json):
        self.jTool = JsonToolFaceRecog.Instance();
        self.jTool.loadJson(input_json)
    
    # private method
    def video2ImgTpl(self, video, uniqueID):
        if os.path.exists(video) == False : 
            self.errorOccur("input video file does not exist.")
        videoPtr = cv2.VideoCapture(video)
        videoFrameID = 0
        frameNeedsExtract = 0 
        imgTpl_list = []
        signatureFaceImage = None

        # get step range
        extract_from_frame, extract_to_frame = self.jTool.getFrameRangeForStep(EXTRACT_FACE_STEP_ID)
        if extract_from_frame >=0:
            frameNeedsExtract = extract_from_frame

        while True:
            [result,img] = videoPtr.read()
            if not result:
                break
            if videoFrameID >= extract_from_frame and videoFrameID <= extract_to_frame:
                if frameNeedsExtract == videoFrameID:
                    imgTpl = ImageTpl()
                    if imgTpl.extract(self.faceRecognizer, img, videoFrameID):
                        if signatureFaceImage is None:
                            signatureFaceImage = img
                        frameNeedsExtract += EXTRACT_FACE_FRAME_SKIP
                        imgTpl.setImageUniqueID('videoID_'+uniqueID+'_frameID_'+str(videoFrameID))
                        imgTpl_list.append(imgTpl)
                    else :
                        frameNeedsExtract += 1
            videoFrameID += 1
        if len(imgTpl_list) <= 0 :
            self.errorOccur("cannot generate template from input video file.")
        return imgTpl_list, signatureFaceImage
        
        
    def video2patient(self):
        patient = Patient()
        patient.from_video = True
        patient.uniqueID = self.jTool.UNIQUE_VIDEO_ID
        patient.tpls, patient.signatureImage = self.video2ImgTpl(self.jTool.INPUT_VIDEO_PATH,self.jTool.UNIQUE_VIDEO_ID)
        patient.setTplPath(self.jTool.SELF_TEMPLATE_PATH)
        return patient
        
        
    # private method   
    def path2patient(self, path):
        patient = Patient()
        patient.from_video = False
        subPaths = walkFolderWithLevel(path, 0)
        diskTplArray = []
        for subPath in subPaths:
            diskTpl = DiskTpl()
            if diskTpl.extract(self.faceRecognizer, subPath):
                diskTplArray.append(diskTpl)
            if patient.tpl_path == "":
                patient.setTplPath(subPath)
        if len(subPaths) == 0:
            patient.setPriviousImagePath(path)
        patient.tpls = diskTplArray
        return patient
    

    def disk2patient(self, mode):
        if mode == MatchModeEnum.MATCH_SELF:
            return self.path2patient(self.jTool.SELF_TEMPLATE_PATH)
        elif mode == MatchModeEnum.MATCH_OTHER:
            patientList = []
            for PATH in self.jTool.OTHER_TEMPLATE_PATH:
                patientList.append(self.path2patient(PATH))
            return patientList
        else:
            return None
 
           
    def match(self, mode, patientFromVideo, patientFromDisk):
        if mode == MatchModeEnum.MATCH_SELF:
            features, label = patientFromDisk.getFeatures()
            if len(features) <= 0 :
                FinalResult.Instance().mode = RecogModeEnum.ENROLL
            else:
                FinalResult.Instance().mode = RecogModeEnum.VERIFY
            SelfMatchAlgorithm().match(self.faceRecognizer, patientFromVideo, patientFromDisk)
        elif mode == MatchModeEnum.MATCH_OTHER:
            for pDisk in patientFromDisk:
                OtherMatchAlgorithm().match(self.faceRecognizer, patientFromVideo, pDisk)
    
    def postProcess(self, videoSelf , diskSelf, diskOthers):
        shouldSaveTpl = True
        if diskSelf.is_match != None : 
            if diskSelf.is_match == False and FinalResult.Instance().mode == RecogModeEnum.VERIFY:
                shouldSaveTpl = False
        for other in diskOthers:
            if other.is_match :
                shouldSaveTpl = False
        #if shouldSaveTpl:
            
        self.saveTpl(videoSelf.tpls, self.jTool.SELF_TEMPLATE_PATH)
        
        if FinalResult.Instance().mode == RecogModeEnum.ENROLL:
            self.saveFaceImages(videoSelf.signatureImage, self.jTool.UNBLURRED_FACE_IMAGE_PATH, self.jTool.BLURRED_FACE_IMAGE_PATH)
            self.saveImages(videoSelf.signatureImage, self.jTool.UNBLURRED_CURRENT_IMAGE_PATH, self.jTool.CURRENT_IMAGE_PATH, self.jTool.BLURRED_CROPPED_IMAGE_PATH)
        else:
            self.saveImages(videoSelf.signatureImage, self.jTool.UNBLURRED_CURRENT_IMAGE_PATH, self.jTool.CURRENT_IMAGE_PATH, self.jTool.BLURRED_CROPPED_IMAGE_PATH)
    
    # private method
    def saveFaceImages(self, image, faceImagePath, faceUnblurredImagePath):
        blurImage = blurImgPatch(image)
        cv2.imwrite(faceImagePath, blurImage)
        cv2.imwrite(faceUnblurredImagePath, image)

    # private method
    def saveImages(self, image, currentImagePath, currentUnblurredImagePath, blurredCroppedImagePath):
        blurImage = blurImgPatch(image)
        cv2.imwrite(currentImagePath, blurImage)
        cv2.imwrite(currentUnblurredImagePath, image)
        cv2.imwrite(blurredCroppedImagePath, blurImage)

    # private method
    def saveImage(self, image,  blurredCroppedImagePath):
        blurImage = blurImgPatch(image)
        cv2.imwrite(blurredCroppedImagePath, blurImage)
        
    # private method  
    def saveTpl(self, tpl_list , toPath):
        numTplAlreadyExist = len(walkFolderWithLevel(toPath, 0))
        if numTplAlreadyExist < MAX_NUM_SAVE_TPL:
            for imgTpl in tpl_list:
                imgTpl.saveTemplate(self.faceRecognizer, toPath)
        
      
    
    def errorOccur(self, errorMessage):
        FinalResult.Instance().error = errorMessage
        FinalResult.Instance().success = False
        self.printState2Json()
        exit(2)
    
    
    def printJson(self, patietnSelf = None, patientOthers = None):
        self.printState2Json(patietnSelf, patientOthers)

    
    
    # private method
    def printState2Json(self, patientSelf = None, patientOthers = None):
        finalResult = FinalResult.Instance()
        outputJson = JsonTool()
        outputJson.insertData("result", "success" if finalResult.success else "failure")
        messageJson = JsonTool()
        messageJson.insertData("error", finalResult.error)
        messageJson.insertData("mode", finalResult.mode)
        messageJson.insertData("blurred_current_image_path", self.jTool.CURRENT_IMAGE_PATH)
        messageJson.insertData("unblurred_current_image_path", self.jTool.UNBLURRED_CURRENT_IMAGE_PATH)
        messageJson.insertData("use_as_template", FinalResult.Instance().use_as_template)
        if patientSelf != None: 
            messageJson.insertData("patient_self", patientSelf.getJson().getStoreData() )
        if patientOthers != None:
            patientOther = []        
            for poj in patientOthers:
                patientOther.append(poj.getJson().getStoreData())
            messageJson.insertData("patient_other", patientOther)
        outputJson.insertData("message", messageJson.getStoreData())
        json_str = json.dumps(outputJson.getStoreData())
        print json_str
        
      
        
"""
MatchAlgorithm Data Structure
======================
Base Object : MatchAlgorithm
Sub Object : SelfMatchAlgorithm; OtherMatchAlgorithm
"""
class MatchAlgorithm:
    def match(self, patientFromVideo, patientFromDisk):
        # explicitly set it up so this can't be called directly
        raise NotImplementedError('Exception raised, Features is supposed to be an interface / abstract class!')
    
    def crossMatch(self, fr, patientFromVideo, patientFromDisk, threshold, shouldRecordScore = False):
        results = []
        featureA, labelA = patientFromVideo.getFeatures()
        featureB, labelB = patientFromDisk.getFeatures()
        i = 0 
        for feature1 in featureA:
            j = 0
            for feature2 in featureB:
                label, probability = fr.match(feature1, feature2, threshold=threshold, needNormalize=True)
                results.append([label[0], probability[0]])
                if shouldRecordScore:
                    patientFromVideo.scoreNote(str(labelA[i]), str(labelB[j]), probability[0])
                j += 1
            i += 1
        return results
    
    '''
    simple match judgement rule, as long as one match, considerd as same person
    Used in self compare
    '''
    def matchRule_simpleMatch(self, results):
        average = 0.0 
        index = 0
        for rlt in results:
            if rlt[0]:
                return True, rlt[1]
            index += 1
            average += rlt[1]
        if index==0 :
            return True, 0   # self match default to be True
        return False, average/index
    
    '''
    overall match judgement rule, calculate the percentage of True label, if more than confidence_threshold (default 70%), then considerd as same person
    While used in self comparison: defaultReturn == True  ; confidence_threshold = 0.3
    Used in others comparison: defaultReturn == False ; confidence_threshold = 0.4
    '''
    def matchRule_overallConfidence(self, results, defaultReturn=False, confidence_threshold=0.4):
        total = 0 
        true_label = 0.0
        average = 0.0
        for rlt in results:
            total += 1
            average += rlt[1]
            if rlt[0]:
                true_label += 1
        if total ==0:
            return defaultReturn, 0   # others match default to be False
        return (true_label/total > confidence_threshold) , average/total


   
class SelfMatchAlgorithm(MatchAlgorithm):
    def match(self, fr, patientFromVideo, patientFromDisk):
        matchResults = self.crossMatch(fr, patientFromVideo, patientFromDisk, ConfigValue.Instance().self_match_single_image_thresh , True)
        patientFromDisk.is_match, patientFromDisk.score = self.matchRule_overallConfidence(matchResults, True, ConfigValue.Instance().self_match_cross_match_percent)
        patientFromDisk.tpls = None
        
    
class OtherMatchAlgorithm(MatchAlgorithm):
    def match(self, fr, patientFromVideo, patientFromDisk):
        matchResults = self.crossMatch(fr, patientFromVideo, patientFromDisk, ConfigValue.Instance().other_match_single_image_thresh)
        patientFromDisk.is_match, patientFromDisk.score = self.matchRule_overallConfidence(matchResults, False, ConfigValue.Instance().other_match_cross_match_percent)
        patientFromDisk.tpls = None
        