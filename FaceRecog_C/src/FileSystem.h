/*
 * FileSystem.h
 *
 *  Created on: Oct 25, 2013
 *      Author: lei
 */

#ifndef FILESYSTEM_H_
#define FILESYSTEM_H_


#include <boost/filesystem.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/xml_parser.hpp>






using namespace std;
using namespace boost::filesystem;
using boost::property_tree::ptree;
using boost::property_tree::read_json;
using boost::property_tree::write_json;



class FileSystem {
private :
	ostringstream bufString;
	string parameter_config_path ;

	//string path_prefix;
	string blur_current_save_image_path;
	string unblur_current_save_image_path;
	string blurred_cropped_img_path;
	string video_path ;
	string unique_video_id;
	string template_self_path;
	vector<string> template_other_path;
	vector<int> step_id_vec;
	vector<string> step_folder_name;
	vector<int> frame_id_vec;

	ptree pTree_root, pTree_message, pTree_self, pTree_other,pTree_child;
	string fileSystemException;



	vector<string> fileCreated;

	string generateCurrentSaveImageFilename(string videopath, string ext);
public:

	static string search_template_folder_name;
	static string search_step_folder_name;
	static string replace_folder_name;
	static string blur_save_image_ext;
	static string unblur_save_image_ext;
	static string mode;
	static string use_as_template;
	static string step_prefix;
	string RESULT;
	string MESSAGE;
	string ENROLL;
	string VERIFY;
	string ERROR_MESSAGE;
	string MODE ;
	string USE_AS_TEMPLATE;
	string PATIENT_SELF;
	string PATIENT_OTHER;
	string IS_MATCH;
	string SCORE;
	string STEP;
	string PATH;
	string UNIQUE_VIDEO_ID;
	string BLUR_CURRENT_IMAGE_PATH;
	string UNBLUR_CURRENT_IMAGE_PATH;
	string BLUR_PREVIOUS_IMAGE_PATH;
	string UNBLUR_PREVIOUS_IMAGE_PATH;

	string SUCCESS;
	string FAILURE;
	string TEMPLATE_EXTENSION;

	int RECOG_SCORE_THRESHOLD_SELF;
	int RECOG_SCORE_THRESHOLD_OTHER;
	int RECOG_SCORE_THRESHOLD_SAVING_TEMPLATE;
	int MAX_SAVE_IMAGE;
	int MAX_SAVE_IMAGE_ONE_VIDEO;



	void printAll();
	int parsingJSON(const char* json_file_path);
	int parsingJSON(const char* json_context, int i);
	int parsingXML(string xml_file_path);
	int writeJSON(string attribute, string value, int whichTree);
	int writeJSON_Error(string errorMessage);
	string getJSON();
	int writeJSON(string attribute, int value, int whichTree);
	FileSystem();
	virtual ~FileSystem();

	string getBlurCurrentSaveImagePath();
	string getUnblurCurrentSaveImagePath();
	string getBlurCroppedImagePath();
	string getParameterConfigPath();
	string getTemplateSelfPath();
	string getUniqueVideoId();
	string getVideoPath();
	vector<string> getStepFolderName();
	vector<int> getStepIdVec();
	vector<int> getFrameIdVec();
	vector<string> getTemplateOtherPath();
	string getFileSystemException();
	string templatePath2imagePath(string templatePath, bool isBlur);



};

#endif /* FILESYSTEM_H_ */
