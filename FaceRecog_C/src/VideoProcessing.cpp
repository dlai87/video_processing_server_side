/*
 * VideoProcessing.cpp
 *
 *  Created on: Oct 3, 2013
 *      Author: lei
 */

#include "VideoProcessing.h"


#include <boost/filesystem.hpp>
using namespace boost::filesystem;



const int MAX_NUM_TEMPLATE_FILES = 5;

// private method
void VideoProcessing::createStepsBaseOnVideoInfo(){
	int size = fileSystem->getTemplateSelfPath().size();
	string lastElement = fileSystem->getTemplateSelfPath().substr(size-1, 1);
	templates_path = fileSystem->getTemplateSelfPath().c_str();
	step_id_vec = fileSystem->getStepIdVec();
	frame_id_vec = fileSystem->getFrameIdVec();

	for (vector<int>::size_type i = 0; i < step_id_vec.size(); i++) {
		stringstream ss;
		if(lastElement == "/")
			ss << templates_path << "step_" << step_id_vec.at(i);
		else
			ss << templates_path << "/step_" << step_id_vec.at(i);
		step_folder_name.insert(step_folder_name.end(), ss.str());
	}
}

// private method
void VideoProcessing::createTemplateFoldersBaseOnSteps(){
	// if the templates folder does not exist, create template folders first
	if(checkPath(templates_path)!= 1){
		mkdir(templates_path, 0777);
	}
	// check if sub folders exist, create sub folders for each steps if it is necessary
	for(vector<string>::size_type i = 0 ; i < step_folder_name.size(); i++){
		const char* path = step_folder_name.at(i).c_str();
		if(checkPath(path)!= 1){
			mkdir(path, 0777);
		}
//		int rlt = countFolderContains(path, ".get");
	}
}


VideoProcessing::VideoProcessing() {
	// TODO Auto-generated constructor stub
	input_video_path = NULL;
	templates_path = NULL;


}

VideoProcessing::~VideoProcessing() {
	// TODO Auto-generated destructor stub
}


int VideoProcessing::init(FileSystem *fileSystem, Face2* face) {
	this->fileSystem = fileSystem;
	this->face = face;
	createStepsBaseOnVideoInfo();
	createTemplateFoldersBaseOnSteps();
	return 0;
}




void VideoProcessing::printAll(){
	cout << "templates_path " << templates_path << endl;
	for(vector<int>::size_type i = 0 ; i < step_id_vec.size(); i++){
		cout << "vector " << step_id_vec.at(i) << ", " << frame_id_vec.at(i) << endl;
	}
}



int VideoProcessing::checkPath(const char* path) {
	if (access(path, 0) == 0) {
		struct stat status;
		stat(path, &status);
		if (status.st_mode & S_IFDIR) {
			return 1; // folder exist.
		} else {
			return 2; // the path is not a folder
		}
	} else {
		return -1; // folder not exist
	}
}


// count the number of a specific kind of file in the folder.
// return: how many files of the specific externsion contained in this folder
// exception: -2, file path not exist
// exception: -1, file path is not directory
/*vector<path> VideoProcessing::countFolderContains(const char* filepath, const char* externsion){
	path p (filepath);
	path ext (externsion);
	vector<path> filelist;
	int count = 0 ;
	try{
		if(exists(p)){
			if(is_directory(p)){
				//get all the file in that directory
				copy(directory_iterator(p), directory_iterator(),back_inserter(filelist));
				//loop the file list, count the number of specific file type
				for(vector<path>::size_type i = 0 ; i < filelist.size(); i++){
					if(filelist.at(i).extension() == ext){
						count ++;
					}
				}
			}else{
				// given filepath is not directory
				return filelist;
			}
		}else{
			// given filepath does not exist
			return filelist;
		}
	}catch(const filesystem_error &ex){
		fileSystem->writeJSON_Error(ex.what());
		exit(1);
	}
	//return counting result
	return filelist;
}*/




vector<ImgTpl*> VideoProcessing::readVideo(const char* videoPath) {
	int frame_count = 0;
	int frame_extract_template = 0;
	int i = 0 ;
	string currentFolderPath = step_folder_name.at(i);

	CvCapture* capture = cvCreateFileCapture(videoPath);
	IplImage* frame;
	frame = cvQueryFrame(capture);
	vector<ImgTpl*> imageList;
	while (1) {
		frame = cvQueryFrame(capture);
		if (!frame){
			break;
		}

		if (i < frame_id_vec.size() && frame_count > frame_id_vec.at(i)) {
			if (i < step_folder_name.size()) {
				currentFolderPath = step_folder_name.at(i);
				i++;
			}
		}
		if(frame_count == frame_extract_template ){
			ImgTpl * imgTpl = new ImgTpl(fileSystem, face);
			IplImage* cloneImage = cvCloneImage(frame);
			bool success = imgTpl->processOneImage(cloneImage);
			imgTpl->setSaveFolder(currentFolderPath);
			if(success){ // if success extract template
				frame_extract_template+=5;
				imageList.insert(imageList.end(), imgTpl);

			}else{
				if(imgTpl!=NULL){
					delete(imgTpl);
					imgTpl = NULL;
				}
				frame_extract_template +=1;
			}
		//	cvReleaseImage(&cloneImage);
		}
		frame_count++;
	}

	if(capture!=NULL){
		cvReleaseCapture(&capture);
		capture = NULL;
	}
	if(frame!=NULL){
		cvReleaseImage(&frame);
		frame = NULL;
	}


	return imageList;
}


/*

vector<ImageTpl*> VideoProcessing::readHardDisk(const char* rootPath) {
	vector<ImageTpl*> imageList;

	vector<path> folderList;

	path p_root(rootPath);

	try {
		copy(directory_iterator(p_root), directory_iterator(),
				back_inserter(folderList));
	} catch (const filesystem_error& ex) {
		fileSystem->writeJSON_Error(ex.what());
	//	fileSystemErrorMessage.append(ex.what() + '\n');
	}

	for (vector<path>::size_type i = 0; i != folderList.size(); ++i) {

		vector<path> fileList;
		try {
			copy(directory_iterator(folderList[i]), directory_iterator(),
					back_inserter(fileList));
		} catch (const filesystem_error& ex) {
			fileSystemErrorMessage.append(ex.what() + '\n');
		}

		for (vector<path>::size_type j = 0; j != fileList.size(); ++j) {
			ImageTpl * myImage = new ImageTpl(fileSystem);
			string folder = folderList[i].string();
			myImage->setSaveFolder(folder);
			myImage->setFilename(fileList[j].string());
	//		myImage->readTemplate();
			imageList.insert(imageList.end(), myImage);
	//		cout << "folder " << folderList[i] << " file " << fileList[j] <<endl;
		}
	}

	return imageList;
}



vector<vector<ImageTpl*> > VideoProcessing::readHardDisk(vector<string> otherTemplatePath){

	vector<vector<ImageTpl*> > otherTemplateList;
	for(vector<string>::size_type i = 0 ; i != otherTemplatePath.size(); i++){
		const char* template_path = otherTemplatePath.at(i).c_str();
		vector<ImageTpl*> temp_list = readHardDisk(template_path);
		otherTemplateList.insert(otherTemplateList.end(), temp_list);
	}
	return otherTemplateList;
}
*/
vector<string> VideoProcessing::readHardDisk2String(const char* rootPath) {
	vector<string> imageList;

	vector<path> folderList;

	path p_root(rootPath);


	try {
		copy(directory_iterator(p_root), directory_iterator(),
				back_inserter(folderList));
	} catch (const filesystem_error& ex) {
		fileSystem->writeJSON_Error(ex.what());
	}

	for (vector<path>::size_type i = 0; i != folderList.size(); ++i) {

		vector<path> fileList;
		try {
			copy(directory_iterator(folderList[i]), directory_iterator(),
					back_inserter(fileList));
		} catch (const filesystem_error& ex) {
			fileSystemErrorMessage.append(ex.what() + '\n');
		}

		for (vector<path>::size_type j = 0; j != fileList.size(); ++j) {
			//		cout << "ext " << fileList[j].extension() << fileList[j].extension().compare(fileSystem->TEMPLATE_EXTENSION) << endl;
			if (fileList[j].extension().compare(fileSystem->TEMPLATE_EXTENSION)
					== 0) {
				imageList.insert(imageList.end(), fileList[j].string());
				//		cout << "folder " << folderList[i] << " file " << fileList[j] <<endl;
			}

		}

	}


	return imageList;
}

vector<vector<string> > VideoProcessing::readHardDisk2String(
		vector<string> otherTemplatePath) {
	vector<vector<string> > otherTemplateList;
	for (vector<string>::size_type i = 0; i < otherTemplatePath.size(); i++) {
		const char* template_path = otherTemplatePath.at(i).c_str();
		vector<string> temp_list = readHardDisk2String(template_path);
		otherTemplateList.insert(otherTemplateList.end(), temp_list);
	}
	return otherTemplateList;
}



