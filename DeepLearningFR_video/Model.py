from Util import *
from FaceRecognizer import *



@Singleton
class FinalResult(object):
    def initDefaultValue(self):
        self.success = True
        self.error = "no_error"
        self.mode = RecogModeEnum.NONE
        self.use_as_template = False
        self.blurred_current_image_path = ""
        self.unblurred_current_image_path = ""
    
        
    def errorOccur(self, errorMessage):
        self.error = errorMessage
        self.success = False
        #self.printState2Json()
        exit(2)

class Patient(object):
    def __init__(self):
        self.uniqueID = ""
        self.from_video = False
        self.signatureImage = None
        self.tpl_path = ""
        self.unblurred_current_image_path = ""
        self.blurred_previous_image_path = ""
        self.tpls = []
        #self.features = []
        self.match_video = True
        self.is_match = False
        self.score = 0 

    def setPriviousImagePath(self, path):
        path = (path[:path.rfind("/")]).replace("template", "uploads/image")
        self.blurred_previous_image_path = path+"/face-blur.jpg"
        self.unblurred_current_image_path = path+"/face.jpg"


    def setTplPath(self, path):
        if path[-1]=="/":
            path = path[:-1]
        self.tpl_path = path
        self.uniqueID = find_between(path, "videoID_", "_frameID_")
        self.setPriviousImagePath(path)
        
    def getFeatures(self):
        features = []
        label = []
        for tpl in self.tpls:
            features.append(self.tpl2Feature(tpl.rawtpl))
            label.append(tpl.mark)
        return features, label
        
    # private method
    def tpl2Feature(self, tpl):
        feature = None
        for eachTpl in tpl:
            if feature is None:
                feature = eachTpl
            else:
                feature = np.hstack((eachTpl, feature))
        return feature
        
    def scoreNote(self, thisTplLabel, otherTplLabel, score, mode = "self_match"):
        if self.from_video:
            for tpl in self.tpls: 
                if tpl.mark == thisTplLabel:
                    if mode == "self_match":
                        tpl.insertSelfScoreDict(otherTplLabel, score)


    def getJson(self):
        jsonTool = JsonTool()
        jsonTool.insertData("is_match", "true" if self.is_match else "false")
        jsonTool.insertData("score", str(self.score))
        jsonTool.insertData("step", "")
        jsonTool.insertData("path", self.tpl_path)
        jsonTool.insertData("unique_video_id", self.uniqueID)
        jsonTool.insertData("blurred_previous_image_path", self.blurred_previous_image_path)
        jsonTool.insertData("unblurred_previous_image_path", self.unblurred_current_image_path)  
        return jsonTool
        
"""
Tpl Data Structure
======================
Base Object : Tpl
Sub Object : ImageTpl; DiskTpl
"""
class Tpl:
    """ Inteface / Abstract Class concept for readability. """
    def extract(self, source):
        # explicitly set it up so this can't be called directly
        raise NotImplementedError('Exception raised, Tpl is supposed to be an interface / abstract class!')
          
class ImageTpl(Tpl):
    def extract(self, fr, source, frameID):
        self.mark = str(frameID)
        self.image = source
        self.rawtpl = fr.extractTemplate(source, detectFace=True)
        self.patientSelfScoreDict = {}
        self.patientOtherScoreDict = {}
        return self.rawtpl is not None
        
    def setImageUniqueID(self, uniqueID):
        self.uniqueID = uniqueID
        
    def saveTemplate(self, fr, path):
        if self.meetMinRequirement( ConfigValue.Instance().save_template_thresh):
            if self.rawtpl is not None:
                savePath = os.path.join(path, self.uniqueID)
                fr.saveTemplates( self.rawtpl, savePath)
                if FinalResult.Instance().use_as_template == False:  # save used as template status from False to True, (if it is already True, do not set it back to False)
                    FinalResult.Instance().use_as_template = True 

    # private method
    def meetMinRequirement(self, minSaveThreshold):
        for key, value in self.patientSelfScoreDict.iteritems(): 
            if value > minSaveThreshold:
                return True
        if not self.patientSelfScoreDict: # dictionary is empty
            return True
        return False


    def insertSelfScoreDict(self, label, score):
        self.patientSelfScoreDict[label] = score


        
class DiskTpl(Tpl):
    def extract(self, fr, source):
        self.rawtpl = fr.readTemplates(source)
        self.mark = str(source)
        return self.rawtpl is not None