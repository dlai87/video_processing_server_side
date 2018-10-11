import os, subprocess
import random
import shutil
import cv2
from copy import copy


def is_valid_file(parser, arg):
    """Check if arg is a valid file that already exists on the file
       system.
    """
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def walk(path):
    imageSet = []
    total = 0 
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".bmp") != -1 or fileName.find(".jpg") != -1 or fileName.find(".png") != -1):
                imageSet.append(fileName)
                total += 1
    return imageSet, total


def cleanfolder(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    
def subtract_lists(a, b):
    """
    >>> a = [0, 1, 2, 1, 0]
    >>> b = [0, 1, 1]
    >>> subtract_lists(a, b)
    [2, 0]

    >>> import random
    >>> size = 10000
    >>> a = [random.randrange(100) for _ in range(size)]
    >>> b = [random.randrange(100) for _ in range(size)]
    >>> c = subtract_lists(a, b)
    >>> assert all((x in a) for x in c)
    """
    a = copy(a)
    for x in b:
        if x in a:
            a.remove(x)
    return a


def randomSelectData(args):
	if args.training_data_size > 0 :
		cleanfolder(args.train_folder)
		cleanfolder(args.test_folder)
		imageSet, total = walk(args.input_file)
		if args.training_data_size < total:
			trainSet = random.sample(imageSet, args.training_data_size)
			testSet = subtract_lists(imageSet ,trainSet)
			for filename in trainSet:
				shutil.copy2(filename, args.train_folder)
			for filename in testSet: 
				shutil.copy2(filename, args.test_folder)
		else:
			print "total data size is smaller than what you want to select"
    


def getImageName(source_string, replace_what):
	head, sep, tail = source_string.rpartition("/")
	return tail


def image_flip(args):
	if args.flip_mode > 0:
		imageSet, total = walk(args.input_file)
		flip_h_path = args.output_file + "/flip_h/"
		if not os.path.exists(flip_h_path):
			os.makedirs(flip_h_path)
		for image_path in imageSet:
			image = cv2.imread(image_path)
			image_flip_h = cv2.flip(image, 0)
			cv2.imwrite(flip_h_path + "H_" + getImageName(image_path, "/"), image_flip_h )
			if args.flip_mode > 1:
				flip_v1_path = args.output_file + "/flip_v1/"
				if not os.path.exists(flip_v1_path):
					os.makedirs(flip_v1_path)
				flip_v2_path = args.output_file + "/flip_v2/"
				if not os.path.exists(flip_v2_path):
					os.makedirs(flip_v2_path)
				image_flip_v1 = cv2.flip(image, 1)
				image_flip_v2 = cv2.flip(image, -1)
				cv2.imwrite(flip_v1_path + "V1_" + getImageName(image_path, "/"), image_flip_v1 )
				cv2.imwrite(flip_v2_path + "V2_" +getImageName(image_path, "/"), image_flip_v2)


def get_parser():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_file",
                        dest="input_file",
                        type=lambda x: is_valid_file(parser, x),
                        help="input image folder")
    parser.add_argument("-o", "--output_file",
                        dest="output_file",
                        type=lambda x: is_valid_file(parser, x),
                        help="output image folder")
    parser.add_argument("-flip_mode", 
                        dest="flip_mode",
                        default=0,
                        type=int,
                        help="flip image mode: 0 == no flip; 1 == flip horizontal only; 2 flip horizontal and vertical")
    parser.add_argument("-training_data_size",
                        dest="training_data_size",
                        default=0,
                        type=int,
                        help="how many data will be random trained, if 0, then not do random selection")
    parser.add_argument("-train_folder",
                        dest="train_folder",
                        default="train",
                        help="folder where to put training data")
    parser.add_argument("-test_folder",
                        dest="test_folder",
                        default="test",
                        help="folder where to put testing data, which is the rest of data")
    
    return parser




if __name__ == "__main__":
    args = get_parser().parse_args()
    print "start"
    image_flip(args)
    randomSelectData(args)
    print "completed"