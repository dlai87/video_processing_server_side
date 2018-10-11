import os 
import glob
import time
import numpy as np
import cv2


def isImgFile(baseFileName):
    """
    Check with the input file name is an image
    isImgFile -> Bool
    baseFileName: "1.jpg"
    """
    [base, ext] = os.path.splitext(baseFileName)
    ext = ext.lower()
    extentions = ['.bmp', '.jpg', '.png', '.tiff', '.tif', '.ppm', '.pgm']
    return ext in extentions


def getImgByFolder(folderName, pattern=None):
    """
    Read images from a folder as a dictionary. The result is {"Tom":[/mnt/1.jpg, /mnt/2.jpg]}
    getListFromDirectory(folderName) -> dict
    folderName: Has one level of sub-folder. Images of a person is in a sub-folder
    pattern: optional. If specified, the name of the image needs to have a substring of pattern to be included in the dict
    """
    results = {}
    for eachPerson in os.listdir(folderName):
        subFolderFulllPath = os.path.join(folderName, eachPerson)
        if os.path.isdir(subFolderFulllPath):
            name = os.path.join(subFolderFulllPath, '*.*')
            t_files = glob.glob(name)
            files = []
            # remove non images and create full path of the image file
            for t_file in t_files:
                if isImgFile(t_file):
                    if pattern is not None:
                        if pattern in t_file:
                            files.append(os.path.join(subFolderFulllPath, t_file))
                    else:
                        files.append(os.path.join(subFolderFulllPath, t_file))
            if len(files) > 0:
                results[eachPerson] = files 
    return results


def mergeDictionaryOfList(dict1, dict2):
    """
    mergeDictionaryOfList(dict1, dict2) -> dict
    dict1: {a:[1], b[2]}
    dict2: {a:[2], c[3]}
    -> dict: {a:[1,2], b:[2], c:[3]}
    """
    results = dict1.copy()
    for eachPerson in dict2.keys():
        if eachPerson in dict1.keys():
            results[eachPerson] = results[eachPerson] + dict2[eachPerson]
        else:
            results[eachPerson] = dict2[eachPerson]
    return results


def readFeaturesFromImg(imageName, strToReplace, targetLoc, modelNames, baseTemplateName='0.tpl'):
    """
    readFeaturesFromImg(imageName, strToReplace, targetLoc, modelNames, baseTemplateName='0.tpl') - > nparray [1, n * featureLength]
    Given a file name, replace strToReplace with targetLoc to get template folder.
    Use model names to read corresponding templates and concontenate them together to obtain a long feature vector.
    imageName: /ubuntu/img/1.jpg
    strToReplace: img
    targetLoc: template
    modelNames: [whole_face, "0.1_0.1"]
    It will read from /ubuntu/img/1.jpg/whole_face/0.tpl and /ubuntu/img/1.jpg/0.1_0.1/0.tpl and concantenate them into one vector. 
    """
    tmplNames = imgPathToTmplPaths(imageName, modelNames, strToReplace, targetLoc)
    finalTemplate = None
    for eachTmplName in tmplNames:
        tempTmplName = os.path.join(eachTmplName, baseTemplateName)
        if not os.path.exists(tempTmplName):
            print "%s dooes not exist" % tempTmplName
            return None 
        templTmpl = (np.load(tempTmplName))
        if finalTemplate is None: 
            finalTemplate = templTmpl
        else:
            finalTemplate = np.hstack((templTmpl, finalTemplate))
    return finalTemplate


def combineTwoFeatures(f1, f2):
    return np.absolute(f1 - f2)


def readImgPairToFeatures(allImgPairs, strToReplace, targetLoc, modelNames, baseTemplateName='0.tpl'):
    """
    Give a pair of images, read its
    """
    img = allImgPairs[0][0]
    tempFeature = readFeaturesFromImg(img, strToReplace, targetLoc, modelNames, baseTemplateName)
    tempFeatureCombined = combineTwoFeatures(tempFeature, tempFeature)
    features = np.ndarray(shape=(len(allImgPairs), tempFeatureCombined.shape[1]), dtype=tempFeature.dtype)
    i = 0
    for imagePairs in allImgPairs:
        f0 = readFeaturesFromImg(imagePairs[0], strToReplace, targetLoc, modelNames, baseTemplateName)
        f1 = readFeaturesFromImg(imagePairs[1], strToReplace, targetLoc, modelNames, baseTemplateName)
        features[i] = combineTwoFeatures(f0, f1)
        i += 1
    return features


def createPosSet(imgsGroupedByPerson, numImgsNeeded=-1):
    """
    imgsGroupedByPerson: dictionay obtained by groupImgsByPerson
    return: a list of image pair. (a list of list). Each image pair belongs to the same person.
    """
    results = []
    for eachKey in imgsGroupedByPerson.keys():
        allImgs = imgsGroupedByPerson[eachKey]
        if len(allImgs) >= 2:
            for j in xrange(len(allImgs) - 1):
                results.append(allImgs[j:j + 2])
                if numImgsNeeded > 0:
                    if len(results) >= numImgsNeeded:
                        return results
    return results


def createNegSet(imgsGroupedByPerson, numImgsNeeded):
    """
    imgsGroupedByPerson: dictionay obtained by groupImgsByPerson
    numImgsNeeded: number of negative sample pairs
    return: a list of image pair of different people. (a list of list). Each image pair belongs to two different people.
    """
    results = []
    allPeople = imgsGroupedByPerson.keys()
    while True:
        np.random.shuffle(allPeople)
        i = 0
        while (i < len(allPeople) - 1):
            if (i > 0):
                i = i + 1
            if (i + 1) == len(allPeople): 
                i = len(allPeople) - 2
            p1Imgs = imgsGroupedByPerson[allPeople[i]]
            i = i + 1
            p2Imgs = imgsGroupedByPerson[allPeople[i]]
            np.random.shuffle(p1Imgs)
            np.random.shuffle(p2Imgs)
            results.append([p1Imgs[0], p2Imgs[0]])
            if len(results) == numImgsNeeded:
                return results    


def createSupervisedDataForVerification(trainData, strToReplace, targetLoc, modelNames, baseTemplateName='0.tpl', numNegImgsTimesPosImgs = 1):
    """
    Get images from same person to create pos data.
    Get images from different people to create neg data.
    createSupervisedDataForVerification(trainData) -> features(ndarray(#samples, #features), labels(samples,)
    trainData: dictionay of people with images {a:[/1.jpg, /2,jpg]}
    """
    posTrainImgPairs = createPosSet(trainData)
    negTrainImgPairs = createNegSet(trainData, len(posTrainImgPairs)*numNegImgsTimesPosImgs)

    posTrainFeatures = readImgPairToFeatures(posTrainImgPairs, strToReplace=strToReplace, targetLoc=targetLoc, modelNames=modelNames, baseTemplateName='0.tpl')
    negTrainFeatures = readImgPairToFeatures(negTrainImgPairs, strToReplace=strToReplace, targetLoc=targetLoc, modelNames=modelNames, baseTemplateName='0.tpl')
        
    trainingFeatures = np.vstack((posTrainFeatures, negTrainFeatures))
    trainingLabels = np.hstack((np.ones(posTrainFeatures.shape[0]), np.zeros(negTrainFeatures.shape[0])))
    print "data shape:"
    print trainingFeatures.shape
    print "data labels shape"
    print trainingLabels.shape
    return trainingFeatures, trainingLabels


def createDataForUnSupervisedTraining(trainData, strToReplace, targetLoc, modelNames, baseTemplateName='0.tpl'):
    p_name = trainData.keys()[0]
    t_imgName = trainData[p_name][0]
    tempTrainingVector = readFeaturesFromImg(t_imgName, strToReplace, targetLoc, modelNames)
    numImgs = 0
    for person in trainData.keys():
        imgNames = trainData[person]
        numImgs += len(imgNames)
    trainingVectors = np.ndarray(shape=(numImgs, tempTrainingVector.shape[1]), dtype=tempTrainingVector.dtype)
    i = 0
    for person in trainData.keys():
        for img in trainData[person]:
            trainingVectors[i] = readFeaturesFromImg(img, strToReplace, targetLoc, modelNames)
            i += 1
    return trainingVectors
        

def imgPathToTmplPaths(imgName, modelNames, strToReplace='processed_imgs_divided', targetLoc='tempates_divided'):
    """
    Return: a list of features target locations.
    Given an image name with full path, return a list of templates location that will b e generated from the image.
    # templates is deined by # modelNames. If there are 3 models, then the list will be containing there templates.
    In the image name, strToReplace will be replaced by targetLoc. So the folder name can be easily updated.
    """
    templateRootFolder = imgName.replace(strToReplace, targetLoc)
    results = []
    for eachModel in modelNames:
        results.append(os.path.join(templateRootFolder, eachModel))
    return results 

def getRoiUsingWidthAndHeight(img,xRatio, yRatio, heightRatio,widthRatio):
    [h,w,channels] = img.shape
    rect0= [0,0,w,h]
    rect_new = [int(rect0[0]+xRatio*rect0[2]),int(rect0[1]+yRatio*rect0[3]),int(rect0[2]*widthRatio),int(rect0[3]*heightRatio)]
    return getRoi(img, rect_new)

def getRoi(img,rect):
    roi = img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    return roi

def searchForThreshold(fps, tps, threshes, targetFP):
    vals = fps <= targetFP
    idx = np.where(vals==False)[0][0]-1
    fpV = fps[idx]
    tpV = tps[idx]
    threshold = threshes[idx]
    return tpV, fpV, threshold

def extractImgsFromVideo(videoName, imgFolder, skipFirstNFrames=1, processEveryNrames=30):
    print "Processing video %s" % videoName
    [tempFolderName, tempVideoName] = os.path.split(videoName)
    capture = cv2.VideoCapture(videoName)
    detectArea = []
    runningFlag = True
    i = -1
    while runningFlag:
        ret, img = capture.read()
        i = i + 1
        if i < skipFirstNFrames:
            continue
        if i % processEveryNrames != 0:
            continue
        if ret: 
            i = int(round(time.time() * 1000))
            imgName = os.path.join(imgFolder, str(i)+'.jpg')
            if not os.path.exists(imgFolder):
                os.makedirs(imgFolder)
            cv2.imwrite(imgName, img)
        else:
            runningFlag = False

def getDataByPerson(baseFolder):
    """
    getVideoFoldersByPerson(baseFolder) -> dict
    baseFolder: The folder contains subfolder. Each subfolder is a person folder. Within person folder it is either template or image.
    if baseFolder /mnt/
    return {/mnt/1:[/mnt/1/1.jpg, /mnt/1/1.jpg], /mnt/2:[/mnt/2/1.jpg, /mnt/2/1.jpg]} or     return {/mnt/1:[/mnt/1/tmpl1, /mnt/1/tmpl2]} tmpl1 might be a subfolder

    """
    allPeople = glob.glob(os.path.join(baseFolder, '*'))
    results = {}
    for eachPerson in allPeople:
        results[eachPerson] = glob.glob(os.path.join(eachPerson, '*'))
    return results

def getImgFileNames( path) :
    fileNames = [];
    for dirPath, dirs, files in os.walk(path) :
        for name in dirs + files :
            fullName = os.path.join(dirPath, name)
            if isImgFile(fullName):
                fileNames.append(fullName)
    return fileNames