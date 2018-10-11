import cv2
import dlib
import numpy
import Util
from Util import *


class FaceAligner:
    def __init__(self, pointFile= absolutePathFile('target_points.npy') , shapeFile=absolutePathFile('target_shape.npy') ):
    #def __init__(self, shapeFile='target_shape.npy'):
        shapeArr = numpy.load(shapeFile)
        self.targetShape = (shapeArr[0], shapeArr[1], shapeArr[2])
        FACE_POINTS = list(range(17, 68))
        MOUTH_POINTS = list(range(48, 61))
        RIGHT_BROW_POINTS = list(range(17, 22))
        LEFT_BROW_POINTS = list(range(22, 27))
        RIGHT_EYE_POINTS = list(range(36, 42))
        LEFT_EYE_POINTS = list(range(42, 48))
        NOSE_POINTS = list(range(27, 35))
        JAW_POINTS = list(range(0, 17))
        self.minDimension = 240
        self.ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS + RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(  absolutePathFile('shape_predictor_68_face_landmarks.dat'))
        self.points1 = numpy.matrix(numpy.load(pointFile))
        self.points1 = self.points1.astype(numpy.float64)[self.ALIGN_POINTS]
        self.c1 = numpy.mean(self.points1, axis=0)
        self.points1 -= self.c1
        self.s1 = numpy.std(self.points1)
        self.points1 /= self.s1

    def resizeImg(self, img):
        [h, w, n] = img.shape
        tempVal = h
        if (w < h):
            tempVal = w
        if tempVal > self.minDimension:
            ratio = float(self.minDimension) / tempVal
            im = cv2.resize(img, ((int)(w * ratio), (int)(h * ratio)))
            return im
        else:
            return img

    def get_landmarks(self, im):
        rects = self.detector(im, 1)
        if len(rects) > 1:
            return None
        if len(rects) == 0:
            return None
        return numpy.matrix([[p.x, p.y] for p in self.predictor(im, rects[0]).parts()])

    def visualizeLandMarks(self, img, points):
        for i in xrange(points.shape[0]):
            cv2.circle(img, (points[i, 0], points[i, 1]), 1, (255, 255, 0), 1)
        cv2.imshow('1', img)
        cv2.waitKey(0)

    def transformation_from_points(self, points2):
        points2 = points2.astype(numpy.float64)[self.ALIGN_POINTS]
        c2 = numpy.mean(points2, axis=0)
        points2 -= c2
        s2 = numpy.std(points2)
        points2 /= s2
        U, S, Vt = numpy.linalg.svd(self.points1.T * points2)
        R = (U * Vt).T
        return numpy.vstack([numpy.hstack(((s2 / self.s1) * R, c2.T - (s2 / self.s1) * R * self.c1.T)), numpy.matrix([0., 0., 1.])])

    def warp_im(self, im, M):
        output_im = numpy.zeros(self.targetShape, dtype=im.dtype)
        cv2.warpAffine(im,
                       M[:2],
                       (self.targetShape[1], self.targetShape[0]),
                       dst=output_im,
                       borderMode=cv2.BORDER_TRANSPARENT,
                       flags=cv2.WARP_INVERSE_MAP)
        return output_im

    def transformImg(self, img):
        img = self.resizeImg(img)
        landmarks1 = self.get_landmarks(img)
        if landmarks1 is not None:
            M = self.transformation_from_points(landmarks1)
            warped_mask = self.warp_im(img, M)
            return warped_mask
        else:
            return None


def getPoints():
    fileName = 'std_face_r3.jpg'
    im1 = cv2.imread(fileName, cv2.IMREAD_COLOR)
    faceAligner = FaceAligner()
    landmarks1 = faceAligner.get_landmarks(im1)
    a = numpy.load(absolutePathFile('target_points.npy'))
    faceAligner.visualizeLandMarks(im1, a)
    sp = numpy.asarray(im1.shape)
    numpy.save(absolutePathFile('target_points'), landmarks1)
    numpy.save(absolutePathFile('target_shape'), sp)


def testWrap():
    faceAligner = FaceAligner()
    im2 = cv2.imread('gaoyuanyuan.jpg', cv2.IMREAD_COLOR)
    warped_mask = faceAligner.transformImg(im2)
    cv2.imwrite('img.jpg', warped_mask)


if __name__ == '__main__':
    testWrap()
