# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 13:36:27 2015

@author: dehua
"""



import subprocess
import os
import json


#config_xml = 'parameter-config.xml'
face_recog_file = '/Release/FaceRecog_refactor'
decrypt_jar = 'DecryptFiles.jar'
template_root_path = '/home/aicu01admin/apps/aiview_dashboard_ror_nida/current/public/system/template/'
video_root_path = '/home/aicu01admin/apps/aiview_dashboard_ror_nida/current/public/system/uploads/video/'
#template_root_path = '/home/lei/test_data/system/template/'
#video_root_path = '/home/lei/test_data/system/uploads/video/'
out_file_name = 'outputs.txt'
patient_list = ['patient6',
                'patient8'
		""",
                'patient10',
                'patient12',
                'patient14',
                'patient16',
                'patient18',
                'patient20',
                'patient22',
                'patient23',
                'patient25',
                'patient27',
                'patient28',
                'patient30'
		"""
		]
                


def generate_param_xml():
    param_folder = "./param/"
    xml_template = open(param_folder+"parameter-config.template", "r")
    data = xml_template.read()
    data_str = str(data)
    
    confident = 0
    qulity = 0
    max_roll = 0
    max_yaw = 0
    
    xmls = []
    while confident < 50:
        confident += 10
        qulity = 0
        while qulity < 128:
            qulity += 64
            max_roll = 0
            while max_roll < 40:
                max_roll += 10
                max_yaw = 0
                while max_yaw < 30:
                    max_yaw += 10
                    s = data_str.replace('VALUE_FACE_CONFI_THRESH', str(confident))
                    s = s.replace('VALUE_FACE_QUALI_THRESH', str(qulity))
                    s = s.replace('VALUE_MAX_ROLL', str(max_roll))
                    s = s.replace('VALUE_MAX_YAW', str(max_yaw))
                    filename = param_folder + "parameter-config_"+str(confident)+"_"+str(qulity)+"_"+str(max_roll)+"_"+str(max_yaw)+".xml"
                    print filename
                    xmls.append(filename)
                    temp = open(filename, "w")
                    temp.write(s)
                    temp.close();
    xml_template.close()
    return xmls
    
    
def walk(path):
    fileSet = []
    total = 0 
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find(".flv") != -1 and fileName.find("blur") == -1 and fileName.find("mux")==-1 ):
                if (fileName.find("dev") == -1):
                    decryptFile = fileName+'dev.flv'
                    if os.path.exists(decryptFile) == False:
                        arg = 'java -jar '+decrypt_jar + ' ' + fileName + ' ' + decryptFile
                        p = subprocess.Popen(arg, stdout=subprocess.PIPE,shell=True)
                        out, err = p.communicate()
                    fileSet.append(decryptFile)
                    total += 1
    return fileSet
    
def clean(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            fileName = os.path.join(root, file)
            if (fileName.find("dev.flv") != -1 ):
                print 'rm ' + fileName
                p = subprocess.Popen('rm ' + fileName, stdout=subprocess.PIPE,shell=True)
                out, err = p.communicate()
    

def prepareJson(input_video, self_template_path, all_template, config_xml):
    input_json = '"{\\"parameter_config_xml_path\\":\\"'+config_xml
    input_json +='\\",\\"input_video_path\\":\\"' + input_video 
    input_json += '\\",\\"self_template_path\\":\\"' +template_root_path + self_template_path + '\\",'
    input_json += '\\"other_template_path\\":[' 
    for path in all_template:
        if path != self_template_path:
            input_json += '{\\"template_path\\":\\"'+template_root_path+path+'\\"},'
    input_json = input_json[0:len(input_json)-1]
    input_json += '],'
    input_json += '\\"video_info\\":[],'
    input_json +='\\"current_image_path\\":\\"' + template_root_path + self_template_path +'/xxx-blur.jpg\\",'
    input_json +='\\"unblurred_current_image_path\\":\\"' +template_root_path + self_template_path+ '/xxx.jpg\\"}"'
    
    return input_json

def runFaceRecog(input_json):
    args = face_recog_file +' '+ input_json
#    print args
    p = subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE,shell=True)
    out, err = p.communicate()
    return out, err
    
def handleResult(video , ouput_json, report, s, ms, mo):
   # print output_json
    data = json.loads(ouput_json)
    result = data["result"]
    error = data["message"]["error"]
    
    
    if result=="success":
        s +=1
        mode = data["message"]["mode"]
        match_self  = data["message"]["patient_self"]["is_match"]
    
        others = data["message"]["patient_other"]
        report.write(result + ' | ' + error + ' | ' + mode + ' | ' + match_self + ' | ' )
        match_other = "0"
        for other in others:
            if other["is_match"]!="0":
                match_other = "1"
        if match_self=="0" and mode != "enroll":
            print 'self not match'
            report.write(video +' | ' + ouput_json)
        else:
            ms += 1
            print '====self match======='
        if match_other=="0":
            print 'other not match'
        else:
            mo +=1
            print '===other match====='
            report.write(video +' | ' + ouput_json)
        report.write(match_other + '\n' )
    else:
        report.write(result + ' | ' + ouput_json + '\n' )
    return s,ms,mo


def process_main(config_xml):
    total = 0   
    MATCH_SELF = 0 
    MATCH_OTHER = 0 
    SUCCESS = 0 
    output_file = open(config_xml + out_file_name, 'w') 
    output_file.write('result  | error | mode | match_self | match_other\n' )
    for patient in patient_list:
        videolist = walk(video_root_path+patient)
        for video in videolist:
            input_json = prepareJson(video, patient,patient_list,config_xml )
            print input_json
            output_json, err = runFaceRecog(input_json)
            print output_json
            SUCCESS, MATCH_SELF, MATCH_OTHER = handleResult(video, output_json, output_file, SUCCESS, MATCH_SELF, MATCH_OTHER)
            total += 1
    output_file.write('SUMMARY:\n' )
    output_file.write('total#:'+str(total)+'\n' )
    output_file.write('success#:'+ str(SUCCESS)+'\n' )
    output_file.write('match_self#:' + str(MATCH_SELF)+'\n' )
    output_file.write('match_other#:' +str(MATCH_OTHER)+'\n' )
    output_file.close() 
    for patient in patient_list:
        clean(video_root_path+patient)
    
    
xmls = generate_param_xml()
for xml in xmls:
    process_main(xml)
