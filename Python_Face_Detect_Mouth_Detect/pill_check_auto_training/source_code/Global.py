# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 11:49:34 2015

@author: lei
"""
import os


SHOW_IMG = False
DETECT_MOUTH_AREA_FLAG = False
DRAW_FACE_TRACKING = True
STEP_NEED_PILL_CHECK = 1
STEP_NEED_PILL_COUNT = -1  #STEP ID NEED TO COUNT PILL NUMBER, PLACEHOLDER 
current_path = os.path.dirname(os.path.abspath(__file__))

svm_predict_path = current_path + "/libsvm-3.18/svm-predict"
MODEL_FILE = "" 
OUTPUT = "out.txt"
medication_type = "med"
feature_file_path = ""


PILL_COLOR_WHITE_RATIO_TREASH = 0.05