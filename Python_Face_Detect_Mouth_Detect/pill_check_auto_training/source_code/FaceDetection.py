import cv2
import os
import cv
import sys
import json
import PillShapeChecker
import PillColorChecker
import copy
import Global
import FaceMouthDetect
import logging
import time
import subprocess
import xml.etree.ElementTree as ET


#example input json:



# example output json :
#{"result":"success","message": {"error_message":"null", "info" : [{"step_id" : 0, "frame_id" : 0, "error_type" : "wrong_pill_shape/wrong_pill_color/face_missing/mouth_missing"}]}}

        


class VideoInfo:
    def __init__(self, step_id, step_type,frame_id,pos_x,pos_y,pos_w,pos_h,save_image_name ):
        self.step_id = step_id
        self.step_type = step_type
        self.frame_id = frame_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_w = pos_w
        self.pos_h = pos_h
        self.save_image_name = save_image_name
    def getVideoInfo(self):
        return  self.step_id, self.step_type, self.frame_id,self.pos_x,self.pos_y, self.pos_w,self.pos_h,self.save_image_name 
        

class VideoProcessor:
    """
    Read frames from a video file, blur the videos.
    Blur necessary frames and unblur specific ROI at a specific frame.
    Extract specific frame image in the process as well.
    """
    def __init__(self, log = None):
        self.VIDEO_INFO = []
        
        self.kernelSZ = 28
        self.wrongPillColorDetected = -1
        self.wrongPillShapeDetected = -1
        self.lineThickness= 3
        self.color = (0,255,0,0)
        self.fps = 15
        self.videoWriter = None
        self.xLEnlarge=-0.2
        self.xREnlarge=-0.2
        self.yTEnlarge=-0.2
        self.yBEnlarge=-0.2
      #  self.codec = cv.FOURCC('I','Y','U','V')
        self.codec = cv.FOURCC('F','L','V','1')
        self.error_info = []
        self.videoFrameID = 0 
        self.videoDuration = 0
        self.faceMissingErrorFreq = self.getFaceMissingErrorFreq()   

        
        
    def getFaceMissingErrorFreq(self):
        params = ET.parse(Global.current_path+'/pill_detect_parameter.xml').getroot() 
        freq = 0
        for param in params.findall('param'):
            if(param.get('name')=='face_missing_error_freq'):
                freq = int(param.text)
        return freq
        
        
    def initVideo(self):
        self.videoName = self.INPUT_VIDEO_PATH
        self.processedVideoName = self.BLUR_VIDEO_PATH
        self.TEMP_AVI = self.processedVideoName + '.avi'
        self.feature_file = self.processedVideoName + '.feature.txt'
        assert os.path.exists(self.videoName), self.throwExcept("%s not exist" % self.videoName)
        #self.finish("failure", "%s not exist" % self.videoName, self.error_info)
        self.videoDuration = self.getLength(self.videoName)
        self.videoPtr = cv2.VideoCapture(self.videoName)
        if ".mp4" in self.videoName:
            self.fps = 24
        
    def getLength(self, filename):
        result = subprocess.Popen([self.FFPROBE_PATH, filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        string = [x for x in result.stdout.readlines() if "Duration" in x][0]
        substr = self.getTimeInMillicSec(string)
        return substr
       
    def getTimeInMillicSec(self, string):
        time = 0
        substr = self.find_between(string, "Duration: ", ", start")
        times = substr.replace(':',' ').replace('.',' ').split()
        time = int(times[3])*10+int(times[2])*1000+(int)(times[1])*60*1000+(int)(times[0])*60*60*1000
        return time
        
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
        
    def throwExcept(self,exceptMessage):
        raise Exception(exceptMessage) 
        
    def parseJSON(self, input_json):
        data = json.loads(input_json)
        self.USERNAME = data["username"]
        self.INPUT_VIDEO_PATH = data["input_video_path"]
        self.BLUR_VIDEO_PATH = data["blur_video_path"]
        self.MEDICATION_TYPE = data["medication_type"]
        self.STEP_MED_PILL_COUNT = data["step_med_pill_count"]
        self.FFPROBE_PATH = data["ffprobe_path"]
     #   self.SVM_MODEL_PATH = data["svm_model_path"]
        temp_video_info = data["video_info"]
        
        for step in temp_video_info:
            video_info = VideoInfo(step["step_id"], step["type"], step["frame_id"], step["pos_x"], step["pos_y"], step["pos_w"], step["pos_h"], step["save_image_name"])
            self.VIDEO_INFO.append(video_info)
        

    def findFrameInfo(self, frame):
        for videoInfo in self.VIDEO_INFO:
            step_id, step_type, frame_id,pos_x,pos_y, pos_w,pos_h,save_image_name = videoInfo.getVideoInfo()
            if frame_id == frame and step_type == "Obj_Detected" and step_id != 6:
                return [step_id, step_type, frame_id,pos_x,pos_y, pos_w,pos_h,save_image_name]
            if step_id == 6 : # step == DISSOLVE_COUNT_DOWN, just save the step start image
                if frame_id == frame and step_type == "Step_Start":
                    return [step_id, step_type, frame_id,pos_x,pos_y, pos_w,pos_h,save_image_name]
        return []
    
   
    
    def blurImgPatch(self,inputImg):
        """
        Blur an image patch
        """
        [height,width,channels] = inputImg.shape
        blurKernel = width
        if width > self.kernelSZ and height > self.kernelSZ:
            blurKernel = self.kernelSZ
        else:
            if blurKernel > height:
                blurKernel = height  
        outputImg = cv2.blur(inputImg,(blurKernel,blurKernel))
        return outputImg
    
    def blurImg(self,inputImg,x,y,width,height,xLEnlarge,xREnlarge,yTEnlarge,yBEnlarge):
        """
        if width or height is 0, blurred the whole image.
        if width or height is bigger than 0,
        first change the ROI based on enlargeRatio.
        Then blur region that are notwithin roi
        """
        if width == 0 or height ==0:
            blurredImg = self.blurImgPatch(inputImg)
            return[blurredImg,0,0,0,0]
        if width>0 or height>0:
            [imgH,imgW,chanles] = inputImg.shape
            [newX,newY,newW,newH] = FaceMouthDetect.adjustROI(x,y,width,height,xLEnlarge,xREnlarge,yTEnlarge,yBEnlarge)
            [newX,newY,newW,newH] = FaceMouthDetect.checkRange(newX,newY,newW,newH,imgW,imgH)
            x0 = newX
            x1 = newX + newW
            y0 = newY
            y1 = newY + newH  
            inputImg[0:imgH+1,0:x0+1]=self.blurImgPatch(inputImg[0:imgH+1,0:x0+1])  
            inputImg[0:imgH+1,x1:imgW+1]=self.blurImgPatch(inputImg[0:imgH+1,x1:imgW+1])  
            inputImg[0:y0+1,x0:x1+1]=self.blurImgPatch(inputImg[0:y0+1,x0:x1+1]) 
            inputImg[y1:imgH+1,x0:x1+1]=self.blurImgPatch(inputImg[y1:imgH+1,x0:x1+1]) 
        return [inputImg,newX,newY,newW,newH]

    
    def ImageBlur(self, frameInfo, img):
        roiImg = img[0:0,0:0]
        cropImg = img[0:0,0:0]
        
        if len(frameInfo) > 0:
            x = frameInfo[3]
            y = frameInfo[4]
            width = frameInfo[5]
            height = frameInfo[6]
            [img,newX,newY,newW,newH] = self.blurImg(img,x,y,width,height,self.xLEnlarge,self.xREnlarge,self.yTEnlarge,self.yBEnlarge)
            cropImg = copy.copy(img)   
            roiImg = copy.copy(img)
            roiImg = roiImg[y:y+height, x:x+width]
            if newH > 0 and newW > 0:
                cropImg = cropImg[ newY:newY+newH, newX:newX+newW] 
            
            FaceMouthDetect.drawRect(img,[newX,newY,newW,newH])              
        else:
            [img,newX,newY,newW,newH] = self.blurImg(img,0,0,0,0,0,0,0,0)
            cropImg = copy.copy(img) 
        return img, cropImg, roiImg
        
    def secondLevelPillChecker(self, frameInfo, enlargeCropImg, nonEnlargeRoiImg):
        
        if len(frameInfo) > 0:
            if frameInfo[0] == Global.STEP_NEED_PILL_CHECK:   # if step_id is 1 (pill_id step)
                Global.feature_file_path = self.feature_file
                Global.medication_type = self.MEDICATION_TYPE
                if PillShapeChecker.run(enlargeCropImg):
                    self.wrongPillShapeDetected = 0
                else:
                    if PillShapeChecker.run(nonEnlargeRoiImg):
                        self.wrongPillShapeDetected = 0
                    else:
                        self.wrongPillShapeDetected = 1
                        temp_info = [frameInfo[0],frameInfo[2],"wrong_pill_shape"]
                        self.error_info.append(temp_info)
                if PillColorChecker.run(enlargeCropImg):
                    self.wrongPillColorDetected = 0
                else:
                    if PillColorChecker.run(nonEnlargeRoiImg):
                        self.wrongPillColorDetected = 0
                    else:
                        self.wrongPillColorDetected = 1
                        temp_info = [frameInfo[0],frameInfo[2],"wrong_pill_color"]
                        self.error_info.append(temp_info)
        return self.wrongPillShapeDetected, self.wrongPillColorDetected
    
    def pillAmountChecker(self, frameInfo, cropImg):
        if len(frameInfo) > 0:
            if frameInfo[0] == Global.STEP_NEED_PILL_COUNT:   # if step_id is 1 (pill_id step)
                if True:
                    pass
                else:
                    temp_info = [frameInfo[0],frameInfo[2],"ADDITIONAL_PILLS"]
                    self.error_info.append(temp_info)
                
    
    def reportFaceMouthError(self, frame, facePos, mouthPos):
        if len(facePos)<=0 and self.shouldReportFaceMissing(frame):
            temp_info = [self.calStepBasedOnFrame(frame),frame,"face_missing"]
            self.error_info.append(temp_info)
        if len(mouthPos)<=0 and Global.DETECT_MOUTH_AREA_FLAG:
            temp_info = [self.calStepBasedOnFrame(frame),frame,"mouth_missing"]
            self.error_info.append(temp_info)
        return self.error_info
        
        
        
    def shouldReportFaceMissing(self, frameID):
        stepsToBeSkipped = [1]  # 1 == pill_id_step
        step_id = self.calStepBasedOnFrame(frameID)
        if step_id in stepsToBeSkipped:
            return False
        if self.faceMissingErrorFreq == 0:
            return True
        if frameID % self.faceMissingErrorFreq == 0:
            return True
        return False
        
        
        
    def calStepBasedOnFrame(self, currFrame):
        index = len(self.VIDEO_INFO)
        if index <= 0:
            return 0
        while index > 1:
            index -= 1
            currVideoInfo = self.VIDEO_INFO[index]
            step_id_1, step_type, frame_id_1,pos_x,pos_y, pos_w,pos_h,save_image_name = currVideoInfo.getVideoInfo()
            preVideoInfo = self.VIDEO_INFO[index-1]
            step_id_0, step_type, frame_id_0,pos_x,pos_y,  pos_w,pos_h,save_image_name = preVideoInfo.getVideoInfo()
            if(currFrame <= frame_id_1 and currFrame>=frame_id_0):
                return step_id_0
        step_id, step_type, frame_id,pos_x,pos_y, pos_w,pos_h,save_image_name = self.VIDEO_INFO[0].getVideoInfo()
        return step_id
                    
        
    def saveCropImage(self, frameInfo, cropImg):
        if len(frameInfo) > 0:
            save_path = frameInfo[len(frameInfo)-1]
            cv2.imwrite(save_path, cropImg)
            
    def finish(self,result,error_message, info=[]):
        output_json = '{"result":'
        output_json += '"'+str(result)+'",'
        output_json += '"message":'
        output_json += '{"error_message":'
        output_json += '"'+str(error_message)+'",'
        output_json += '"total_frame":'
        output_json += str(self.videoFrameID)+','
        output_json += '"video_duration":'
        output_json += str(self.videoDuration)+','
        output_json += '"info":['
        index = 0 
        for info_row in info:
            index += 1
            output_json += '{'
            output_json += '"step_id":'+str(info_row[0])+','
            output_json += '"frame_id":'+str(info_row[1])+','
            output_json += '"error_type":"'+str(info_row[2])
            output_json += '"}' 
            if index != len(info):
                output_json += ',' 
        output_json += ']}}'
        logging.info(output_json)
        print output_json
        return output_json
       
        
    def convertAVI2FLV(self):
        os.rename(self.TEMP_AVI, self.processedVideoName)
        if os.path.exists(self.feature_file):
            os.remove(self.feature_file)
        
        
        
    def processImg(self):
        """
        Example program to show how to use face mouth detector
        """
        faceMouthDetector = FaceMouthDetect.FaceMouthDetector()
       
        #oldRect = None
        while True:
            [result,img] = self.videoPtr.read()
            if not result:
                break
            # detect face and mouth area
            [facePos, mouthPos] = faceMouthDetector.process(img)
            # check face missing and mouth missing errors
            self.reportFaceMouthError(self.videoFrameID,facePos,mouthPos)
            frameInfo = self.findFrameInfo(self.videoFrameID)
            img, cropImg, roiImg = self.ImageBlur(frameInfo, img)
            # check if number of pill in mouth is correct 
            self.pillAmountChecker(frameInfo, cropImg)
            # check pill shape and color
            self.secondLevelPillChecker(frameInfo, cropImg, roiImg)
            # save crop image 
            self.saveCropImage(frameInfo, cropImg)

            
            faceMouthDetector.draw(img, facePos, mouthPos)

           
            self.videoFrameID += 1

            #save video
            if not self.videoWriter:
                [imgH,imgW,chanles] = img.shape
                self.videoWriter = cv2.VideoWriter(self.TEMP_AVI,self.codec,self.fps,(imgW,imgH))
                assert self.videoWriter.isOpened()==True, self.throwExcept("cannot open file %s for writing" % self.processedVideoName)
            if self.videoWriter:
                self.videoWriter.write(img)
                #print self.videoFrameID
                
        self.convertAVI2FLV()

        return self.finish("success", "null", self.error_info)
    

if __name__== '__main__':
    if len(sys.argv)!=2:
        print "Usage: python FaceDetection.py [INPUT_JSON] version 2.0.25 base"
        exit(2)
    if not os.path.exists(Global.current_path +'/log/'):
        os.makedirs(Global.current_path +'/log/')
    logging.basicConfig(filename=Global.current_path + '/log/face_blur_obj_detect_'+time.strftime("%Y-%m-%d")+'.log', level=logging.INFO)
    logging.info("start")
    videoProcessor = VideoProcessor()
    try:
        videoProcessor.parseJSON(sys.argv[1])
        videoProcessor.initVideo()
        videoProcessor.processImg()
    except:
        videoProcessor.finish("failure", sys.exc_info()[1], videoProcessor.error_info) 
    logging.info("finish")