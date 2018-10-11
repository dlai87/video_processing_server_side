/*
 * ImgTpl.cpp
 *
 *  Created on: Dec 23, 2014
 *      Author: dehua
 */

#include "ImgTpl.h"
#include "FileCreatedRecorder.h"

int ImgTpl::currentVideoSaveTemplate = 0 ;

ImgTpl::ImgTpl(FileSystem * fileSystem, Face2* face) {
	this->fileSystem = fileSystem;
	this->face = face;
}

ImgTpl::~ImgTpl() {
	// TODO Auto-generated destructor stub
	if(imageTemp!=NULL){
		NObjectFree(imageTemp);
		imageTemp=NULL;
	}
	if(iplImage!=NULL){
		cvReleaseImage(&iplImage);
		iplImage=NULL;
	}
}

void ImgTpl::setSaveFolder(string saveFolder){
	this->saveFolder = saveFolder;
}

HNBuffer ImgTpl::getImageTemp(){
	return this->imageTemp;
}



bool ImgTpl::processOneImage(IplImage* iplImage) {

	this->iplImage = iplImage;
	return generateTemplate()==0?true:false;
}


int ImgTpl::generateTemplate(){

//	imageTemp = (HNBuffer*) malloc( sizeof(HNBuffer));
	int templateDone = face->extractTemplate(iplImage, &imageTemp);
	// if template generated fail
	if (templateDone != 0) {
		// release memory
		imageTemp = NULL;
	}
	return templateDone;
}


int ImgTpl::saveTemplate(){

	if(saveFolder.size() <= 0){
		return -1;
	}
	if(imageTemp == NULL){
		return -1;
	}

	int num_template = countFolderContains(saveFolder, fileSystem->TEMPLATE_EXTENSION);
	timeval curTime;
	gettimeofday(&curTime, NULL);
	char buffer [80];
	strftime(buffer, 80, "%Y-%m-%d-%H-%M-%S", localtime(&curTime.tv_sec));
	stringstream ss;
	ss << saveFolder << "/"  << buffer << curTime.tv_usec << "-vid-" << fileSystem->getUniqueVideoId() << fileSystem->TEMPLATE_EXTENSION;
	string filename = ss.str();
//	save image condition: total image in the folder no more than MAX_SAVE_IMAGE && current video save no more than MAX_SAVE_IMAGE_ONE_VIDEO
	if(num_template < fileSystem->MAX_SAVE_IMAGE
	&& currentVideoSaveTemplate < fileSystem->MAX_SAVE_IMAGE_ONE_VIDEO){
		FileCreatedRecorder::getInstance()->addFilename(filename);
		if (!WriteAllBytesN(filename.c_str(), imageTemp)) {
				cout << "error occur while WriteAllBytesN " << endl;
				return -2;
		}
		currentVideoSaveTemplate++;
	}
	return 0 ;
}


bool ImgTpl::saveImage(string saveUnblurImagePath, string saveBlurImagePath,  string blurred_cropped_img_path){
	bool status = true;
	if(this->iplImage == NULL){
		status = false;
		return status;
	}


	const char* saveUnblurImageName = saveUnblurImagePath.c_str();
	FileCreatedRecorder::getInstance()->addFilename(saveUnblurImageName);
	cvSaveImage(saveUnblurImageName, this->iplImage, 0);
	const char* saveBlurImageName = saveBlurImagePath.c_str();
	FileCreatedRecorder::getInstance()->addFilename(saveBlurImageName);
	IplImage*  blurImage =  blurImgPatch(this->iplImage);
	cvSaveImage(saveBlurImageName, blurImage, 0);

	if(blurred_cropped_img_path!="null"){
		cvSaveImage(blurred_cropped_img_path.c_str(), blurImage, 0);
	}

	cvReleaseImage(&blurImage);
	blurImage = NULL;

	return status;
}

IplImage* ImgTpl::blurImgPatch(IplImage* inputImg) {
	IplImage* outputImg = cvCloneImage(inputImg);
	int kernelSZ = 60;
	int width = inputImg->width;
	int height = inputImg->height;
	int blurKernel = width;
	if (width > kernelSZ && height > kernelSZ) {
		blurKernel = kernelSZ;
	} else {
		if (blurKernel > height) {
			blurKernel = height;
		}
	}

	if (blurKernel % 2 == 0)
		blurKernel = blurKernel - 1;
	cvSmooth(inputImg, outputImg, CV_BLUR, blurKernel, 0, 0, 0);
	return outputImg;
}

// count the number of a specific kind of file in the folder.
// return: how many files of the specific externsion contained in this folder
// exception: -2, file path not exist
// exception: -1, file path is not directory
int ImgTpl::countFolderContains(string filepath, string externsion){
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
				return 0;
			}
		}else{
			// given filepath does not exist
			return 0;
		}
	}catch(const filesystem_error &ex){
	//	cout << ex.what() << endl;
	}
	//return counting result
	return count;
}
