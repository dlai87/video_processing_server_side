# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 16:36:58 2014

@author: dehua
"""


import numpy as np
import cv2

'''
   input : image
   output : white balanced image
'''
def whiteBalance(img):
    img_temp = img.copy()
    r = cv2.split(img_temp)[0]
    g = cv2.split(img_temp)[1]
    b = cv2.split(img_temp)[2]
    cv2.equalizeHist(r,r)
    cv2.equalizeHist(g,g)
    cv2.equalizeHist(b,b)
    img_temp = cv2.merge([r,g,b]);
    return img_temp

'''
   input :  image
           
           image -> gaussian blur -> color space convert -> white balance
           
   output:  

'''    
def preProcess(img, colorSpaceCode):
    tempImg = img.copy()
    # gaussian blur image
    tempImg = cv2.GaussianBlur(tempImg,(5,5),0)
    if (colorSpaceCode == 'HLS'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2HLS, tempImg)
    if (colorSpaceCode == 'GRAY'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY, tempImg)
    if (colorSpaceCode == 'YUV'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2YUV, tempImg)
    if (colorSpaceCode == 'LAB'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2LAB, tempImg)
    if (colorSpaceCode == 'LUV'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2LUV, tempImg)
    if (colorSpaceCode == 'YCrCb'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2YCR_CB, tempImg)
    if (colorSpaceCode == 'HSV'):
        cv2.cvtColor(tempImg, cv2.COLOR_BGR2HSV, tempImg)
    return whiteBalance(tempImg)

'''
    grab cut with erosion and dilation 
    
    input image, initial rect 

'''
def grabCut(img, rect):
    mask = np.zeros(img.shape[:2],np.uint8)
    bgdModel = np.zeros((1,65), np.float64)
    fgdModel = np.zeros((1,65), np.float64)
    cv2.grabCut(img,mask,rect, bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img = img*mask2[:,:,np.newaxis]
    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(img,kernel,iterations = 1)
    dilation = cv2.dilate(erosion,kernel,iterations = 1)
    return dilation


'''
    

'''
def fusion(img_list, width, height):
    maxValue = 0 
    fusion_img = np.zeros((height,width,3), np.uint8)
    for x0 in range(0,width):
        for y0 in range(0,height):
            for img in img_list:
                if(img[y0,x0][0] != 0 or img[y0,x0][1] != 0 or img[y0,x0][2] != 0):
                    fusion_img[y0,x0][0] = fusion_img[y0,x0][0] + 1
                    fusion_img[y0,x0][1] = fusion_img[y0,x0][1] + 1
                    fusion_img[y0,x0][2] = fusion_img[y0,x0][2] + 1
            if(fusion_img[y0,x0][0] > maxValue):
                maxValue = fusion_img[y0,x0][0]
    return [fusion_img, maxValue]
    
def fusionImageDisplay(img,fusion_image, maxValue, width, height):
    image = img.copy()
    if(maxValue !=0):
        for x0 in range(0,width):
            for y0 in range(0,height):
                if(fusion_image[y0,x0][0] != maxValue ):
                    image[y0,x0][0] = 0
                    image[y0,x0][1] = 0
                    image[y0,x0][2] = 0
    else:
        for x0 in range(0,width):
            for y0 in range(0,height):
                image[y0,x0][0] = 0
                image[y0,x0][1] = 0
                image[y0,x0][2] = 0
    return image
    
    
def score(pixelValue, COLOR_SPACE_RANGE): 
    score = 0 
    H_delta = 10
    L_delta = 10
    S_delta = 10
    H_min = COLOR_SPACE_RANGE[0]
    H_max = COLOR_SPACE_RANGE[1]
    L_min = COLOR_SPACE_RANGE[2]
    L_max = COLOR_SPACE_RANGE[3]
    S_min = COLOR_SPACE_RANGE[4]
    S_max = COLOR_SPACE_RANGE[5]
    H_pixel = pixelValue[0]
    L_pixel = pixelValue[1]
    S_pixel = pixelValue[2]
    print 'H_min '+ str(H_min) + ' H_max ' + str(H_max) + ' L_min ' + str(L_min) + ' L_max ' + str(L_max) + ' H_pixel ' + str(H_pixel) + ' L_pixel ' + str(L_pixel) 
    if(H_pixel >= H_min and H_pixel <= H_max and L_pixel >= L_min and L_pixel <= L_max and S_pixel >= S_min and S_pixel <= S_max):
        score = 2
    else:
        if(H_pixel > (H_min-H_delta) and H_pixel < (H_max+H_delta) and L_pixel > (L_min-L_delta) and L_pixel < (L_max+L_delta) and S_pixel > (S_min-S_delta) and S_pixel < (S_max+S_delta)):
            score = 1
        else:
            score = 0
    return score

def statistic(maskImg):
    H = []
    L = []
    S = []
    for row in maskImg:
        for pixel in row:
            if(pixel[0]!=0 or pixel[1]!=0 or pixel[2]!=0):
                H.append(pixel[0])
                L.append(pixel[1])
                S.append(pixel[2])
    
    H_median = np.median(H)
    H_average = np.average(H)
    H_std = np.std(H)
    L_median = np.median(L)
    L_average = np.average(L)
    L_std = np.std(L)
    S_median = np.median(S)
    S_average = np.average(S)
    S_std = np.std(S)
    print ' H_median '+str(H_median)+' H_average '+str(H_average)+' H_std '+str(H_std)
    print ' L_median '+str(L_median)+' L_average '+str(L_average)+' L_std '+str(L_std)
    print ' S_median '+str(S_median)+' S_average '+str(S_average)+' S_std '+str(S_std)
    
    
def colorConfidence(maskImg, COLOR_SPACE_RANGE):
    confidence = []
    for row in maskImg:
        for pixel in row:
            if(pixel[0]!=0 or pixel[1]!=0 or pixel[2]!=0):
                confidence.append(score(pixel,COLOR_SPACE_RANGE))
    
    in_range = 0 
    near_range = 0 
    out_range =0
    for value in confidence:
        if(value == 2):
            in_range = in_range + 1
        if(value == 1):
            near_range = near_range + 1
        if(value == 0):
            out_range = out_range + 1
    
    total_pixels = in_range + near_range + out_range; 
    confi = 0 
    if(total_pixels != 0 ):
        confi = (in_range + 0.5*near_range) / total_pixels; 
  #  print 'in range '+ str(in_range) + ' near range '+ str(near_range) + ' out range ' + str(out_range)
    return confi
    
def getDynamicLowerParam(array, percent):
    length = len(array[0]) 
    re = sorted(array[0]) 
    cutting_level = re[int((1-percent)*length)]
    return cutting_level
    
def histogram(img):
    roi_h = []
    roi_l = []
    roi_s = []
    for row in img:
        for pixel in row:
            if(pixel[0]!=0 or pixel[1]!=0 or pixel[2]!=0):
                roi_h.append(pixel[0])
                roi_l.append(pixel[1])
                roi_s.append(pixel[2])
    h1, bin_edges  =  np.histogram(roi_h, 10, [0,256])
    h2, bin_edges  =  np.histogram(roi_l, 10, [0,256])
    h3, bin_edges  =  np.histogram(roi_s, 10, [0,256])
    print h1
    print h2
    print h3
    return h
    
    
def main():
    for i in range (1,5001): 
        print i
        ColorSpaceSequences = ['RGB','GRAY','YUV','LAB','LUV','YCrCb']
        # =======> white tictac
        #  output_folder = "C:/Users/dehua/Desktop/images/test/"
        #  imageName = "C:/Users/dehua/Desktop/images/pill_image_acc/tictac (" + str(i) + ").bmp"
        # =======> gray capsule
        #   output_folder = "C:/Users/dehua/Desktop/images/crop/roi_pos/"
        #   imageName = "C:/Users/dehua/Desktop/images/crop/pos/" + str(i) + ".jpg"
        #  ======> neg image
        #   output_folder = "C:/Users/dehua/Desktop/images/test_other_color/"
        #   imageName = "C:/Users/dehua/Desktop/images/pill_image_other_color/other(" + str(i) + ").jpg"
        # =======> white tictac
        output_folder = "C:/Users/dehua/Desktop/images/output/white/"
        imageName = "C:/Users/dehua/Desktop/images/pill_image_acc/white(" + str(i) + ").jpg"
        img = cv2.imread(imageName)
        #cv2.imwrite(output_folder+str(i)+"original.bmp", img);
    
        width = img.shape[1]
        height = img.shape[0]
        x = (int)(0.18*width)
        y = (int)(0.18*height)
        w = (int)(0.8*width)
        h = (int)(0.8*height)

        rect = (x,y,w,h); 
        img_list = []    
    
    #  img_draw = getRect(hls_wb, x,y,w,h)
    #  cv2.imwrite("C:/Users/dehua/Desktop/images/pill_image_acc/hls_wb/rect"+str(i)+".bmp", img_draw);
        for colorSpaceCode in ColorSpaceSequences: 
            preProImg = preProcess(img, colorSpaceCode)
            grabCutImg = grabCut(preProImg, rect)
            img_list.append(grabCutImg)
            cv2.imwrite(output_folder+str(i)+colorSpaceCode+".bmp", grabCutImg);
    
        [img_fusion, maxValue] = fusion(img_list,width,height)
    
   
        maskImg = img.copy()
    
  
        cv2.cvtColor(maskImg, cv2.COLOR_BGR2HLS, maskImg)
        maskImg = whiteBalance(maskImg)
        # cv2.imwrite(output_folder+"fusion/"+str(i)+"_maskImg.jpg", maskImg);
        light = cv2.split(maskImg)[1].reshape(1,-1)
    
        if(maxValue !=0):
            for x0 in range(0,width):
                for y0 in range(0,height):
                    if(img_fusion[y0,x0][0] != maxValue ):
                        maskImg[y0,x0][0] = 0
                        maskImg[y0,x0][1] = 0
                        maskImg[y0,x0][2] = 0
                        img_fusion[y0,x0][0] = img_fusion[y0,x0][0]*250/maxValue
                        img_fusion[y0,x0][1] = img_fusion[y0,x0][1]*250/maxValue
                        img_fusion[y0,x0][2] = img_fusion[y0,x0][2]*250/maxValue
        else:
            for x0 in range(0,width):
                for y0 in range(0,height):
                    maskImg[y0,x0][0] = 0
                    maskImg[y0,x0][1] = 0
                    maskImg[y0,x0][2] = 0
        
        #  hist_img = histogram(maskImg)
        #  cv2.imwrite(output_folder+"fusion/"+str(i)+"maskImg.jpg", maskImg);
    
    # statistic(maskImg)
    # print str(i) + "  ==========  "
    cv2.imwrite(output_folder+"fusion/"+str(i)+"fusion_img.jpg", img_fusion);
 #  cutting_level = getDynamicLowerParam(light, 0.1)
  #  print 'cutting_level  ' + str(cutting_level)
    
   #    parameters:
   #  GREEN:(70.0, 160.0, 255.0, 255.0);
   #  YELLOW:(100, 200, 255.0, 255.0);
   #  ORANGE:(115, 220, 255.0, 255.0);
   #  BLUE:(25, 150, 255.0, 255.0);
   #  RED:(150, 150, 255, 255);


  #  confidence = colorConfidence(maskImg, [0,256,cutting_level,256,0,256])    
 #   print str(i) + " confidence ==========  " + str(confidence);  
 