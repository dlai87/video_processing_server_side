import json
import os
import cv2 
import ConfigParser




class MatchModeEnum(object):
    MATCH_SELF = 1
    MATCH_OTHER = 2

class RecogModeEnum(object):
    ENROLL = "enroll"
    VERIFY = "verify"
    NONE = "none"


def absolutePathFile(filename):
    absolute_path = os.path.dirname(__file__)
    if absolute_path in filename:
        return filename
    if filename[0] == "/":
        return absolute_path + filename
    else:
        return absolute_path + "/" + filename

def throwExcept(exceptMessage):
    raise Exception(exceptMessage)    
    
def walkFolderWithLevel(path, level=0):
    folders = []
    for root, dirs, files in walklevel(path, level):
        for dir in dirs:
            folderName = os.path.join(root, dir)
            folders.append(folderName)
    return folders

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    if not os.path.exists(some_dir):
        os.makedirs(some_dir)
   # assert os.path.isdir(some_dir), throwExcept("%s not exist" % some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
            
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""   
        
def blurImgPatch(inputImg):
    """
    Blur an image patch
    """
    kernelSZ = 28
    [height,width,channels] = inputImg.shape
    blurKernel = width
    if width > kernelSZ and height > kernelSZ:
        blurKernel = kernelSZ
    else:
        if blurKernel > height:
            blurKernel = height  
    outputImg = cv2.blur(inputImg,(blurKernel,blurKernel))
    return outputImg
    

            
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class ConfigValue(object):
    def load(self, path):
        config = ConfigParser.RawConfigParser()
        config.read(path)
        self.self_match_single_image_thresh = float(config.get('value-config', 'self_match_single_image_thresh'))
        self.self_match_cross_match_percent = float(config.get('value-config', 'self_match_cross_match_percent'))
        self.other_match_single_image_thresh = float(config.get('value-config', 'other_match_single_image_thresh'))
        self.other_match_cross_match_percent = float(config.get('value-config', 'other_match_cross_match_percent'))
        self.save_template_thresh = float(config.get('value-config', 'save_template_thresh'))



class JsonTool(object):
    def __init__(self):
        self.storeData = {}
    
    def loadJson(self, inputJson):
        data = json.loads(inputJson)
        
    def insertData(self, key, value ):
        self.storeData[key] = value
        
    def getStoreData(self):
        return self.storeData
        
    def cleanData(self):
        self.storeData = {}
        
    def dumpJson(self):
        json_str = json.dumps(self.storeData)
        return json_str

@Singleton 
class JsonToolFaceRecog(JsonTool):
    def loadJson(self, inputJson):
        data = json.loads(inputJson)
        self.INPUT_VIDEO_PATH = data["input_video_path"]
        self.SELF_TEMPLATE_PATH = data["self_template_path"]
        self.CURRENT_IMAGE_PATH = data["current_image_path"]
        self.UNBLURRED_CURRENT_IMAGE_PATH = data["unblurred_current_image_path"]
        self.BLURRED_CROPPED_IMAGE_PATH = data["blurred_cropped_img_path"]
        self.UNIQUE_VIDEO_ID = data["unique_video_id"]
        self.OTHER_TEMPLATE_PATH = []
        other_templates = data["other_template_path"]
        for other in other_templates:
            self.OTHER_TEMPLATE_PATH.append(other["template_path"])
        self.VIDEO_INFO = []
        video_info_list = data["video_info"]
        for video_info in video_info_list:
            frameInfo = FrameInfo(video_info["step_id"],video_info["frame_id"],video_info["frame_type"] )
            self.VIDEO_INFO.append(frameInfo)
        index_medication = self.UNBLURRED_CURRENT_IMAGE_PATH.index("medication")
        self.UNBLURRED_FACE_IMAGE_PATH = self.UNBLURRED_CURRENT_IMAGE_PATH[0:index_medication] + 'face.jpg'
        self.BLURRED_FACE_IMAGE_PATH = self.CURRENT_IMAGE_PATH[0:index_medication] + 'face-blur.jpg'



    def getFrameRangeForStep(self, step_id):
        start_frame = -1
        end_frame = -1
        for frameInfo in self.VIDEO_INFO:
            if step_id == frameInfo.step_id:
                if "Step_Start" == frameInfo.frame_type:
                    start_frame = frameInfo.frame_id
            else:
                if "Step_Start" == frameInfo.frame_type:
                    if start_frame !=-1 and end_frame ==-1 :
                        end_frame = frameInfo.frame_id
        return start_frame, end_frame



class FrameInfo:
    def __init__(self, step_id, frame_id, frame_type):
        self.step_id = step_id
        self.frame_id = frame_id
        self.frame_type = frame_type



                                  
       

            
          