import unittest
import FaceAligner as FA
import FeatureExtracter as FE
import cv2
import FaceRecognizer as FR
import os 
import shutil
import numpy as np


TEMP_FOLDER = "./temp_test_data_folder"

class TestFR(unittest.TestCase):
    def testFaceAligner(self):
        print "test face aligner"
        faceAligner = FA.FaceAligner()
        im2 = cv2.imread('./test_data/gaoyuanyuan1.jpg', 1)
        warped_mask = faceAligner.transformImg(im2)
        self.assertEqual(warped_mask[0][0][0], 180)

    def testExtractSaveAndLoadFeatures(self):
        print "test extract and save features"
        img1Name = './test_data/gaoyuanyuan1.jpg'
        img1 = cv2.imread(img1Name, 1)
        classifier = FR.XGBClassifier('xgboost.model', scalerFile='xgboost.scaler')
        faceRecognizer = FR.FaceRecognizer(classifier, gpuMode = False)
        tpls1 = faceRecognizer.extractTemplate(img1, detectFace=True)
        self.assertTrue(tpls1[0][0][2]> 8.6)
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
        else:
            shutil.rmtree(TEMP_FOLDER)
            os.makedirs(TEMP_FOLDER)

        print "save templates"
        faceRecognizer.saveTemplates(tpls1, TEMP_FOLDER)
        self.assertTrue(os.path.exists(os.path.join(TEMP_FOLDER, '0.25_0.25_0.5_0.58', '0.tpl')))
        self.assertTrue(os.path.exists(os.path.join(TEMP_FOLDER, '0.2_0.12_0.39_0.55', '0.tpl')))
        self.assertTrue(os.path.exists(os.path.join(TEMP_FOLDER, '0.2_0.12_0.3_0.38', '0.tpl')))
        self.assertTrue(os.path.exists(os.path.join(TEMP_FOLDER, '0.2_0.12_0.6_0.76', '0.tpl')))
        self.assertTrue(os.path.exists(os.path.join(TEMP_FOLDER, 'whole_face', '0.tpl')))

        print "read templates"
        tmpl = faceRecognizer.readTemplates(TEMP_FOLDER) 
        self.assertTrue(tmpl[0][-1] > 13.4072)
        shutil.rmtree(TEMP_FOLDER)

    def testFaceRecognition(self):
        img1Name = './test_data/gaoyuanyuan1.jpg'
        img2Name = './test_data/gaoyuanyuan2.jpg'
        img1 = cv2.imread(img1Name, 1)
        img2 = cv2.imread(img2Name, 1)
        classifier = FR.XGBClassifier('xgboost.model', scalerFile='xgboost.scaler')
        faceRecognizer = FR.FaceRecognizer(classifier, gpuMode = False)
        tpls1 = faceRecognizer.extractTemplate(img1, detectFace=True)
        tpls2 = faceRecognizer.extractTemplate(img2, detectFace=True)

        if tpls1 is None or tpls2 is None:
            print "Cannot detect face"
        else:
            feature1 = None
            feature2 = None
            for eachTpl in tpls1:
                if feature1 is None:
                    feature1 = eachTpl
                else:
                    feature1 = np.hstack((eachTpl, feature1))
            for eachTpl in tpls2:
                if feature2 is None:
                    feature2 = eachTpl
                else:
                    feature2 = np.hstack((eachTpl, feature2))

            label, probability = faceRecognizer.match(feature1, feature2, needNormalize=True)
            self.assertTrue(label)
            self.assertTrue(probability > 0.9999)

if __name__ == '__main__':
    unittest.main()