
from FaceRecognizer import *
from Controller import *

    

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print "Usage: python FaceRecognition.py [INPUT_JSON] version 3.0.0"
        exit(2)
        
    json = sys.argv[1]

    

    controller = Controller()
    controller.loadInputJson(json)

    try:
        
        videoPatient = controller.video2patient()
    
        selfDiskPatient = controller.disk2patient(MatchModeEnum.MATCH_SELF) 
        otherPatientList = controller.disk2patient(MatchModeEnum.MATCH_OTHER) 

        controller.match(MatchModeEnum.MATCH_SELF, videoPatient, selfDiskPatient)
        controller.match(MatchModeEnum.MATCH_OTHER, videoPatient, otherPatientList)
    
        controller.postProcess(videoPatient, selfDiskPatient, otherPatientList)
        controller.printJson(selfDiskPatient, otherPatientList )
    
    except Exception, e:
        controller.errorOccur(str(e.message))
        controller.printJson()
        
    
   