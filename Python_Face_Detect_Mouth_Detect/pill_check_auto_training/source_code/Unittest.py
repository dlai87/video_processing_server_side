# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:51:45 2015

@author: dehua
"""

import unittest
from FaceDetection import VideoProcessor
from FaceDetection import VideoInfo
import numpy as np
import cv2
import cv
import Global
import os
import sys
import json
import FaceMouthDetect
from FaceMouthDetect import FaceMouthDetector
          
          
class TestFaceDetection(unittest.TestCase):
    
    def setUp(self):
        self.init("resource/test.flv")
    
    def init(self, videoName):
        self.videoProcessor = VideoProcessor()
        self.medication_type = "Medication B"
        self.input_video_path = videoName
        self.blur_video_path = "resource/test-blur.flv"
        self.step_med_pill_count = 1
        self.videoInfo1 = VideoInfo(1,"Step_Start",0,0,0,0,0,"resource/save1.jpg")
        self.videoInfo2 = VideoInfo(1,"Obj_Detected",47,94,42,61,66,"resource/save2.jpg")
        self.videoInfo3 = VideoInfo(2,"Step_Start",67,0,0,0,0,"resource/save3.jpg")
        self.videoInfo4 = VideoInfo(2,"Obj_Detected",88,78,148,96,96,"resource/save4.jpg")
        self.videoInfo5 = VideoInfo(3,"Step_Start",90,0,0,0,0,"resource/save5.jpg")
        self.videoInfo6 = VideoInfo(3,"Obj_Detected",95,78,171,51,51,"resource/save6.jpg")
        self.videoInfo = []
        self.videoInfo.append(self.videoInfo1)
        self.videoInfo.append(self.videoInfo2)
        self.videoInfo.append(self.videoInfo3)
        self.videoInfo.append(self.videoInfo4)
        self.videoInfo.append(self.videoInfo5)
        self.videoInfo.append(self.videoInfo6)
        self.json = '{"username":"tester","medication_type":"'+self.medication_type+\
                    '","input_video_path":"'+self.input_video_path+ \
                    '","blur_video_path":"'+self.blur_video_path + '","video_info":['
        index = 0
        for vInfo in self.videoInfo:
            index += 1
            self.json += '{"type":"'+vInfo.step_type+'","save_image_name":"'+vInfo.save_image_name+\
                        '","frame_id":'+str(vInfo.frame_id)+',"step_id":'+str(vInfo.step_id)+',"pos_x":'+str(vInfo.pos_x)+\
                        ',"pos_y":'+str(vInfo.pos_y)+',"pos_w":'+str(vInfo.pos_w)+',"pos_h":'+str(vInfo.pos_h)+'}'
            if index != len(self.videoInfo):
                self.json += ','             
        self.json += '],"step_med_pill_count":'+str(self.step_med_pill_count)+'}'
        self.videoProcessor.parseJSON(self.json)
        
    
    def tearDown(self):
        """
        if os.path.exists(self.blur_video_path):
            os.remove(self.blur_video_path)
        if os.path.exists(self.videoInfo2.save_image_name):
            os.remove(self.videoInfo2.save_image_name)
        if os.path.exists(self.videoInfo4.save_image_name):
            os.remove(self.videoInfo4.save_image_name)
        if os.path.exists(self.videoInfo6.save_image_name):
            os.remove(self.videoInfo6.save_image_name)
        """
        self.videoProcessor = None
    
    def test_parseJSON(self):
        
        self.assertEqual(self.videoProcessor.MEDICATION_TYPE,self.medication_type)
        self.assertEqual(self.videoProcessor.INPUT_VIDEO_PATH,self.input_video_path)
        self.assertEqual(self.videoProcessor.BLUR_VIDEO_PATH,self.blur_video_path)
        self.assertEqual(self.videoProcessor.STEP_MED_PILL_COUNT,self.step_med_pill_count)
        for i in range(0,len(self.videoInfo)-1):
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].step_type,self.videoInfo[i].step_type)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].save_image_name,self.videoInfo[i].save_image_name)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].frame_id,self.videoInfo[i].frame_id)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].step_id,self.videoInfo[i].step_id)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].pos_x,self.videoInfo[i].pos_x)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].pos_y,self.videoInfo[i].pos_y)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].pos_w,self.videoInfo[i].pos_w)
            self.assertEqual(self.videoProcessor.VIDEO_INFO[i].pos_h,self.videoInfo[i].pos_h)
        
    def test_findFrameInfo(self):
        frameInfo = self.videoProcessor.findFrameInfo(0)
        self.assertTrue(len(frameInfo)==0)
        for vInfo in self.videoInfo:
            frameInfo = self.videoProcessor.findFrameInfo(vInfo.frame_id)
            if vInfo.step_type == "Obj_Detected":
                self.assertTrue(len(frameInfo)>0)
            else:
                self.assertTrue(len(frameInfo)==0)
        
        
    def test_ImageBlur(self):
        width = 240
        height = 360
        channel = 3
        img = np.zeros([height,width,channel])
        for vInfo in self.videoInfo:
            frameInfo = self.videoProcessor.findFrameInfo(vInfo.frame_id)
            img, cropImg, roiImg = self.videoProcessor.ImageBlur(frameInfo, img)
            if vInfo.step_type == "Obj_Detected":
                self.assertTrue(cropImg.shape[0] >= vInfo.pos_h)
                self.assertTrue(cropImg.shape[1] >= vInfo.pos_w)
                self.assertTrue(roiImg.shape[0] == vInfo.pos_h)
                self.assertTrue(roiImg.shape[1] == vInfo.pos_w)
            else:
                self.assertTrue(cropImg.shape == img.shape)
    
    @unittest.skip("demonstrating skipping")
    def test_SecondLevelPillChecker(self):
        correct_imgs = ['resource/RIGHT1.png','resource/RIGHT2.bmp']
        wrong_imgs = ['resource/WRONG1.jpg',\
        'resource/WRONG2.jpg','resource/WRONG3.jpg',\
        'resource/WRONG4.jpg','resource/WRONG5.jpg']
        correct_shape_wrong_color_img = ['resource/RIGHT_SHAPE_WRONG_COLOR.jpg']
        coorect_color_wrong_shape_img = ['resource/WRONG_SHAPE1.bmp', 'resource/WRONG_SHAPE2.bmp',\
        'resource/WRONG_SHAPE3.bmp','resource/WRONG_SHAPE4.bmp']
        correctImgs = []
        for url in correct_imgs:
            correctImgs.append(cv2.imread(url))
        wrongImgs = []
        for url in wrong_imgs:
            wrongImgs.append(cv2.imread(url))
        correctShapeWrongColorImgs = []
        for url in correct_shape_wrong_color_img:
            correctShapeWrongColorImgs.append(cv2.imread(url))
        correctColorWrongShapeImgs = []
        for url in coorect_color_wrong_shape_img:
            correctColorWrongShapeImgs.append(cv2.imread(url))
            
        frameInfo = self.videoProcessor.findFrameInfo(self.videoInfo2.frame_id)
        self.videoProcessor.feature_file = './feature.txt'
        
        
        for img in correctImgs:
            shape, color = self.videoProcessor.secondLevelPillChecker(frameInfo,img )
            self.assertEqual(shape,0)
            self.assertEqual(color,0)
        for img in wrongImgs:
            shape, color = self.videoProcessor.secondLevelPillChecker(frameInfo,img )
            self.assertEqual(shape,1)
            self.assertEqual(color,1)
        for img in correctShapeWrongColorImgs:
            shape, color = self.videoProcessor.secondLevelPillChecker(frameInfo,img )
            self.assertEqual(shape,0)
            self.assertEqual(color,1)
        for img in correctColorWrongShapeImgs:
            shape, color = self.videoProcessor.secondLevelPillChecker(frameInfo,img )
            self.assertEqual(shape,1)
            self.assertEqual(color,0)
            
    def test_ReportFaceMouthError(self):        
        Global.DETECT_MOUTH_AREA_FLAG = True
        error_info = self.videoProcessor.reportFaceMouthError(1,[],[])
        self.assertEqual(len(error_info), 1)
        self.assertEqual(error_info[0][1],1)
        self.assertEqual(error_info[0][2],'mouth_missing')
        error_info = self.videoProcessor.reportFaceMouthError(2,['face_pos'],[])
        self.assertEqual(len(error_info), 2)
        self.assertEqual(error_info[1][1],2)
        self.assertEqual(error_info[1][2],'mouth_missing')
        error_info = self.videoProcessor.reportFaceMouthError(66,[],['mouth_pos'])
        self.assertEqual(len(error_info), 2)
        Global.DETECT_MOUTH_AREA_FLAG = False
        error_info = self.videoProcessor.reportFaceMouthError(67,[],[])
        self.assertEqual(len(error_info), 3)
        self.assertEqual(error_info[2][1],67)
        self.assertEqual(error_info[2][2],'face_missing')
        
    def test_CalStepBasedOnFrame(self):
        step = self.videoProcessor.calStepBasedOnFrame(1)
        self.assertEqual(step, 1)
        step = self.videoProcessor.calStepBasedOnFrame(47)
        self.assertEqual(step, 1)
        step = self.videoProcessor.calStepBasedOnFrame(67)
        self.assertEqual(step, 2)
        step = self.videoProcessor.calStepBasedOnFrame(69)
        self.assertEqual(step, 2)
        step = self.videoProcessor.calStepBasedOnFrame(90)
        self.assertEqual(step, 3)
        step = self.videoProcessor.calStepBasedOnFrame(92)
        self.assertEqual(step, 3)
    
    def test_ShouldReportFaceMissing(self):
        shouldReport = self.videoProcessor.shouldReportFaceMissing(1)
        self.assertFalse(shouldReport)
        shouldReport = self.videoProcessor.shouldReportFaceMissing(47)
        self.assertFalse(shouldReport)
        shouldReport = self.videoProcessor.shouldReportFaceMissing(66)
        self.assertFalse(shouldReport)
        shouldReport = self.videoProcessor.shouldReportFaceMissing(67)
        self.assertTrue(shouldReport)
        shouldReport = self.videoProcessor.shouldReportFaceMissing(88)
        self.assertTrue(shouldReport)
    
    @unittest.skip("demonstrating skipping")
    def test_processImg_Success_Case(self):
        if os.path.exists(self.blur_video_path):
            os.remove(self.blur_video_path)
        if os.path.exists(self.videoInfo2.save_image_name):
            os.remove(self.videoInfo2.save_image_name)
        if os.path.exists(self.videoInfo4.save_image_name):
            os.remove(self.videoInfo4.save_image_name)
        if os.path.exists(self.videoInfo6.save_image_name):
            os.remove(self.videoInfo6.save_image_name)
        self.assertTrue(os.path.exists(self.input_video_path))
        self.assertFalse(os.path.exists(self.blur_video_path))
        self.assertFalse(os.path.exists(self.videoInfo2.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo4.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo6.save_image_name))
        #test success case
        try:
            self.videoProcessor.initVideo()
            output_json = self.videoProcessor.processImg()
        except:
            output_json = self.videoProcessor.finish("failure", sys.exc_info()[1], self.videoProcessor.error_info) 
        self.assertTrue(os.path.exists(self.blur_video_path))
        self.assertTrue(os.path.exists(self.videoInfo2.save_image_name))
        self.assertTrue(os.path.exists(self.videoInfo4.save_image_name))
        self.assertTrue(os.path.exists(self.videoInfo6.save_image_name))
        data = json.loads(output_json)
        self.assertEqual(data['result'], 'success')
        self.assertEqual(data['message']['error_message'], 'null')
        
    def test_processImg_Failure_Case(self):
        self.init('videoNotExist.flv')
        if os.path.exists(self.blur_video_path):
            os.remove(self.blur_video_path)
        if os.path.exists(self.videoInfo2.save_image_name):
            os.remove(self.videoInfo2.save_image_name)
        if os.path.exists(self.videoInfo4.save_image_name):
            os.remove(self.videoInfo4.save_image_name)
        if os.path.exists(self.videoInfo6.save_image_name):
            os.remove(self.videoInfo6.save_image_name)
        self.assertFalse(os.path.exists(self.input_video_path))
        self.assertFalse(os.path.exists(self.blur_video_path))
        self.assertFalse(os.path.exists(self.videoInfo2.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo4.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo6.save_image_name))
        try:
            self.videoProcessor.initVideo()
            output_json = self.videoProcessor.processImg()
        except:
            output_json = self.videoProcessor.finish("failure", sys.exc_info()[1], self.videoProcessor.error_info)
        self.assertFalse(os.path.exists(self.blur_video_path))
        self.assertFalse(os.path.exists(self.videoInfo2.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo4.save_image_name))
        self.assertFalse(os.path.exists(self.videoInfo6.save_image_name))
        data = json.loads(output_json)
        self.assertEqual(data['result'], 'failure')
        self.assertIsNot(data['message']['error_message'], 'null')
        self.assertEqual(len(data['message']['info']), 0)
        
        
    
        
        
        
class TestFaceMouthDetection(unittest.TestCase):
    def setUp(self):
        self.init()
    
    def init(self):
        self.faceMouthDetector = FaceMouthDetector()
        
    def tearDown(self):
        self.faceMouthDetector = None
        
    def test_Process(self):
        faceOpenMouthImg = cv2.imread('resource/Rowan-open-mouth.jpg')
        nonfaceImg = cv2.imread('resource/face-blur.jpg')
        faceCloseMouthImg = cv2.imread('resource/face_no_mouth.jpg')
        pos = self.faceMouthDetector.process(faceOpenMouthImg,True)
        self.assertTrue(len(pos[0])>0)
        self.assertTrue(len(pos[1])>0)
        pos = self.faceMouthDetector.process(nonfaceImg, True)
        self.assertTrue(len(pos[0])==0)
        self.assertTrue(len(pos[1])==0)
        pos = self.faceMouthDetector.process(faceCloseMouthImg,True)
        self.assertTrue(len(pos[0])>0)
        self.assertTrue(len(pos[1])==0)

if __name__ == '__main__':
    unittest.main()