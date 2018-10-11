/*
 * FileSystem.cpp
 *
 *  Created on: Oct 25, 2013
 *      Author: DEHUA
 */

#include "FileSystem.h"



/*
 * INPUT FORMAT :
 *
 *{
      "parameter_config_xml_path":"/home/lei/Dropbox/DehuaWorkSpace/video_processing_middleware/FaceRecog_whole/parameter-config.xml",
      "input_video_path": "/home/lei/video_blur/decrypted_0_tictac_0_2013-09-23.flv",
      "self_template_path" :"/home/lei/video_blur/templates/",
      "other_template_path":[
      {"template_path":"/home/lei/Dropbox/image-databases/Trial_4_Converted/2/templates/"},
      {"template_path":"/home/lei/Dropbox/image-databases/Trial_4_Converted/1/templates/"}],
      "video_info": [
      {"step_id" : 0,
      "frame_id" : 22},
      {"step_id" : 1,
      "frame_id" : 42 },
      {"step_id" : 2,
      "frame_id" : 66 },
      {"step_id" : 3,
      "frame_id" : 96 }
  	  ]
      "current_image_path": "/xx/xx/xx"
      "unblurred_current_image_path": "/dwq/wee/fe"
   }

 * */

string FileSystem::search_template_folder_name = "";
string FileSystem::search_step_folder_name = "";
string FileSystem::replace_folder_name = "";
string FileSystem::blur_save_image_ext = "";
string FileSystem::unblur_save_image_ext = "";
string FileSystem::use_as_template="false";
string FileSystem::mode = "";
string FileSystem::step_prefix="step_";

FileSystem::FileSystem() {

	RESULT = "result";
	MESSAGE	= "message";
	ERROR_MESSAGE = "error";
	MODE = "mode";
	USE_AS_TEMPLATE = "use_as_template";
	PATIENT_SELF = "patient_self";
	PATIENT_OTHER = "patient_other";
	IS_MATCH = "is_match";
	SCORE = "score";
	STEP = "step";
	PATH = "path";
	UNIQUE_VIDEO_ID = "unique_video_id";
	SUCCESS = "success";
	FAILURE = "failure";
	BLUR_CURRENT_IMAGE_PATH = "blurred_current_image_path";
	UNBLUR_CURRENT_IMAGE_PATH = "unblurred_current_image_path";
	BLUR_PREVIOUS_IMAGE_PATH = "blurred_previous_image_path";
	UNBLUR_PREVIOUS_IMAGE_PATH = "unblurred_previous_image_path";


}


FileSystem::~FileSystem() {

}

int FileSystem::parsingXML(string xml_file_path) {
	ptree tree;
	try {
		read_xml(xml_file_path, tree);

		ENROLL = tree.get<string>("output.enroll");
		VERIFY = tree.get<string>("output.verify");
		TEMPLATE_EXTENSION = tree.get<string>("output.template_externsion");
		RECOG_SCORE_THRESHOLD_SELF = tree.get<int>("output.recognition_score_threshold_self");
		RECOG_SCORE_THRESHOLD_OTHER = tree.get<int>("output.recognition_score_threshold_other");
		RECOG_SCORE_THRESHOLD_SAVING_TEMPLATE = tree.get<int>("output.recognition_score_threshold_saving_template");
		MAX_SAVE_IMAGE = tree.get<int>("output.max_save_templates");
		MAX_SAVE_IMAGE_ONE_VIDEO = tree.get<int>("output.max_save_templates_one_video");
		FileSystem::search_template_folder_name = tree.get<string>("folder.search_template_folder_name");
		FileSystem::search_step_folder_name = tree.get<string>("folder.search_step_folder_name");
		FileSystem::replace_folder_name = tree.get<string>("folder.replace_folder_name");
		FileSystem::blur_save_image_ext = tree.get<string>("folder.blur_save_image_ext");
		FileSystem::unblur_save_image_ext = tree.get<string>("folder.unblur_save_image_ext");



	} catch (exception const&e) {
	//		cout << "exception caught in reading parameter config xml file : "<<e.what() <<endl;
		string ex = e.what();
		fileSystemException = ex;
		return -1;
	}



	return 0;

}

string FileSystem::templatePath2imagePath(string templatePath, bool isBlur){

	string imagePath = templatePath;
	// clean string from "step_" to the rest
	unsigned found = imagePath.find(FileSystem::step_prefix);
	if(found<= imagePath.size()){
		imagePath.replace( found, string::npos,"");
	}
	// replace "template" to "upload/image"
	unsigned pos = imagePath.find(FileSystem::search_template_folder_name);
	if(pos<=imagePath.size()){
		imagePath.replace( pos, FileSystem::search_template_folder_name.size(),
							FileSystem::replace_folder_name);
	}

	if (!imagePath.empty())
	{
	    char lastChar = *imagePath.rbegin();
	    if (lastChar == '/'){
	    	imagePath = imagePath.substr(0, imagePath.size()-1);
	    }
	}

	// append blur or unblur externsion
	if(isBlur){
		imagePath.append(FileSystem::blur_save_image_ext);
	}else{
		imagePath.append(FileSystem::unblur_save_image_ext);
	}
	return imagePath;
}

int FileSystem::parsingJSON(const char* json_content, int i) {

	stringstream ss;
	ss << json_content << endl;
	try {
		ptree pTree, pTree1, pTree2, pTree3, pTree4;
		read_json(ss, pTree);

		parameter_config_path =
				(pTree.get<string>("parameter_config_xml_path"));

		unique_video_id = (pTree.get<string>("unique_video_id"));
		video_path = (pTree.get<string>("input_video_path"));
		template_self_path = (pTree.get<string>("self_template_path"));


		unblur_current_save_image_path = (pTree.get<string>("unblurred_current_image_path"));
		blur_current_save_image_path = (pTree.get<string>("current_image_path"));
		blurred_cropped_img_path = (pTree.get<string>("blurred_cropped_img_path"));

		pTree1 = pTree.get_child("other_template_path");
		for (ptree::iterator it = pTree1.begin(); it != pTree1.end(); ++it) {
			pTree2 = it->second;
			string templates_path = pTree2.get<string>("template_path");
			template_other_path.insert(template_other_path.end(),
					templates_path);
		}
		//template_path = (pTree.get<string>("templates_path")).c_str();
		pTree3 = pTree.get_child("video_info");
		for (ptree::iterator it = pTree3.begin(); it != pTree3.end(); ++it) {
			pTree4 = it->second;
			int step_id = pTree4.get<int>("step_id");
			int frame_id = pTree4.get<int>("frame_id");
			step_id_vec.insert(step_id_vec.end(), step_id);
			frame_id_vec.insert(frame_id_vec.end(), frame_id);
		}

		if(pTree3.size()==0){
			step_id_vec.insert(step_id_vec.end(), 0);
			frame_id_vec.insert(frame_id_vec.end(), 30);
		}



		for (vector<int>::size_type i = 0; i < step_id_vec.size(); i++) {

			stringstream ss;

			ss << template_self_path << "step_" << step_id_vec.at(i);
			step_folder_name.insert(step_folder_name.end(), ss.str());
		}

		int size = template_self_path.size();
		string lastElement = template_self_path.substr(size -1, 1);
		for (vector<int>::size_type i = 0; i < step_id_vec.size(); i++) {
			stringstream ss;
			if (lastElement == "/")
				ss << template_self_path << "step_" << step_id_vec.at(i);
			else
				ss << template_self_path << "/step_" << step_id_vec.at(i);
			step_folder_name.insert(step_folder_name.end(), ss.str());
		}

	} catch (exception const& e) {
	//	cout << "exception " << e.what() << endl;
		string ex = e.what();
		fileSystemException = ex;
		return -1;
	}

	return 0;
}

string FileSystem::generateCurrentSaveImageFilename(string videopath, string ext){
	int start_pos = videopath.find_last_of("/");
	string temp = videopath.substr(start_pos);
	temp.replace(temp.size()-4,4,ext);
	return temp;
}

int FileSystem::parsingJSON(const char* json_file_path) {

	ptree pTree, pTree1, pTree2;
	try {
		read_json(json_file_path, pTree);

		parameter_config_path =
				(pTree.get<string>("parameter_config_xml_path")).c_str();
		unique_video_id = (pTree.get<string>("unique_video_id")).c_str();
		video_path = (pTree.get<string>("input_video_path")).c_str();
		template_self_path = (pTree.get<string>("self_template_path")).c_str();
		pTree1 = pTree.get_child("other_template_path");
		for (ptree::iterator it = pTree1.begin(); it != pTree1.end(); ++it) {
			pTree2 = it->second;
			string templates_path = pTree2.get<string>("template_path");
			template_other_path.insert(template_other_path.end(),
					templates_path);
		}
		//template_path = (pTree.get<string>("templates_path")).c_str();
	} catch (exception const& e) {
		return -1;
	}
	return 0;
}

void FileSystem::printAll() {
	cout << "parameter_config_path " << parameter_config_path << endl;
	cout << "video_path " << video_path << endl;
	cout << "template_self_path " << template_self_path << endl;

	for (vector<string>::size_type i = 0; i < template_other_path.size(); i++) {
		cout << "template_other_path " << template_other_path.at(i) << endl;
	}
	for (vector<string>::size_type i = 0; i < step_folder_name.size(); i++) {
		cout << "step_folder_name " << step_folder_name.at(i) << endl;
	}
	for (vector<int>::size_type i = 0; i < step_id_vec.size(); i++) {
		cout << "step_id_vec " << step_id_vec.at(i) << endl;
	}
	for (vector<int>::size_type i = 0; i < frame_id_vec.size(); i++) {
		cout << "frame_id_vec " << frame_id_vec.at(i) << endl;
	}

	cout << RESULT << endl;
	cout << ERROR_MESSAGE << endl;
	cout << MODE << endl;
	cout << PATIENT_SELF << endl;
	cout << PATIENT_OTHER << endl;
	cout << IS_MATCH << endl;
	cout << SCORE << endl;
	cout << STEP << endl;
	cout << PATH << endl;

	cout << SUCCESS << endl;
	cout << FAILURE << endl;
	cout << "TEMPLATE_EXTENSION " << TEMPLATE_EXTENSION << endl;
	cout << "MAX_SAVE_IMAGE " << MAX_SAVE_IMAGE << endl;
}

/**
 * write error message to JSON, other values set default value.
 *
 * */

int FileSystem::writeJSON_Error(string errorMessage) {
	writeJSON(RESULT, FAILURE, 0);
	writeJSON(ERROR_MESSAGE, errorMessage, 1);
	writeJSON(MODE, "null", 1);
	writeJSON(USE_AS_TEMPLATE, "false", 1);
	writeJSON(BLUR_CURRENT_IMAGE_PATH, "null", 1);
	writeJSON(UNBLUR_CURRENT_IMAGE_PATH, "null", 1);
//	cout <<"############0#############"<< errorMessage << endl;
//	writeJSON(IS_MATCH, "false", 2);
//	writeJSON(SCORE, "0", 2);
//	writeJSON(STEP, "0", 2);
//	writeJSON(PATH, "null", 2);

//	writeJSON(BLUR_PREVIOUS_IMAGE_PATH, "null", 2);
//	writeJSON(UNBLUR_PREVIOUS_IMAGE_PATH, "null", 2);

	return 0;
}

/**
 * ====================================================================
 *   result:   message:
 *   					error:  mode:  use_as_template:   self:        		other:[					current_image_path:
 *   										               is_match				is_match
 *   										                 score					score
 *   										                  step					step
 *   										                  path					path
 *   										                 previous_image_path		previous_image_path]
 * ======================================================================
 * */

int FileSystem::writeJSON(string attribute, string value, int whichTree) {

	switch (whichTree) {
	case 0:
		pTree_root.put(attribute, value);
		break;
	case 1:
		pTree_message.put(attribute, value);
		break;
	case 2:
		pTree_self.put(attribute, value);
		break;
	case 3:
		pTree_other.put(attribute, value);
		break;
	case 4:
		pTree_child.put(attribute, value);
		break;
	case 5:
		pTree_other.push_back(std::make_pair("", pTree_child));
		break;
	default:
		break;
	}
	return 0;
}

int FileSystem::writeJSON(string attribute, int value, int whichTree) {

	switch (whichTree) {
	case 0:
		pTree_root.put(attribute, value);
		break;
	case 1:
		pTree_message.put(attribute, value);
		break;
	case 2:
		pTree_self.put(attribute, value);
		break;
	case 3:
		pTree_other.put(attribute, value);
		break;
	case 4:
		pTree_child.put(attribute, value);
		break;
	case 5:
		pTree_other.push_back(std::make_pair("", pTree_child));
		break;
	default:
		break;
	}
	return 0;
}

string FileSystem::getJSON() {

	if(pTree_other.empty()){
		writeJSON(IS_MATCH, "false", 4);
		writeJSON(SCORE, "0", 4);
		writeJSON(STEP, "0", 4);
		writeJSON(PATH, "null", 4);
		writeJSON(BLUR_PREVIOUS_IMAGE_PATH, "null", 4);
		writeJSON(UNBLUR_PREVIOUS_IMAGE_PATH, "null", 4);
		writeJSON("", "", 5);
	}
	pTree_message.add_child(PATIENT_SELF, pTree_self);
	pTree_message.add_child(PATIENT_OTHER, pTree_other);
	pTree_root.add_child(MESSAGE, pTree_message);
	write_json(bufString, pTree_root, false);
	return bufString.str();
}

/**
 *
 * private arguments getter
 *
 * */

vector<int> FileSystem::getFrameIdVec() {
	return frame_id_vec;
}

string FileSystem::getParameterConfigPath() {
	return parameter_config_path;
}
vector<string> FileSystem::getStepFolderName() {
	return step_folder_name;
}

vector<int> FileSystem::getStepIdVec() {
	return step_id_vec;
}

vector<string> FileSystem::getTemplateOtherPath() {
	return template_other_path;
}

string FileSystem::getBlurCurrentSaveImagePath(){
//	current_save_image_path = "";
	return blur_current_save_image_path;
}

string FileSystem::getBlurCroppedImagePath(){
	return blurred_cropped_img_path;
}

string FileSystem::getUnblurCurrentSaveImagePath(){
//	current_save_image_path = "";
	return unblur_current_save_image_path;
}

string FileSystem::getTemplateSelfPath() {
	return template_self_path;
}

string FileSystem::getUniqueVideoId() {
	return unique_video_id;
}

string FileSystem::getVideoPath() {
	return video_path;
}

string FileSystem::getFileSystemException(){
	return fileSystemException;
}


