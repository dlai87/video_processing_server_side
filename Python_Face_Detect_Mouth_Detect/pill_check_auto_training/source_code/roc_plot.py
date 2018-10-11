from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

def plotROCForTest():
    fv = FaceVerification.FaceVerification( gpuMode = True)
    fileName = '/home/ubuntu/Dropbox/training/caffe/face_recognition/combine_lfw_chinese/fv_web_imgs/0.1_0.1_0.8_0.8//val.txt'
    imgPath = '/home/ubuntu/face_vr/cropped_imgs_divided/combine_chinese_lfw_0.1_0.1_0.8_0.8/val'
    [imgs1, imgs2, labels] = parseText(fileName)

    confidences = []
    tempLabels = []
    correct = 0
    wrong = 0
    thresholds = 0.666124263643
    for i in xrange(len(imgs1)):
        imgName1 = os.path.join(imgPath, imgs1[i])
        imgName2 = os.path.join(imgPath, imgs2[i])
        tempLabels.append(labels[i])
        img1 = cv2.imread(imgName1)
        img2 = cv2.imread(imgName2)
        t1 = fv.extractTemplate(img1, False)
        t2 = fv.extractTemplate(img2, False)
        [result, tempConfidence] = fv.match(t1,t2)
        if result == tempLabels[i]:
            correct +=1
        else:
            wrong += 1

        print "person %s conf %s targetLabel %s correct %s wrong %s" %(i, tempConfidence, labels[i], correct, wrong)
        confidences.append(tempConfidence)

    fpr, tpr, thresholds = roc_curve(tempLabels, confidences)

    fpr.dump('./test_img/fpr_new')
    tpr.dump('./test_img/tpr_new')
    thresholds.dump('thresholds_new')
    plt.plot(fpr, tpr)
    plt.show()