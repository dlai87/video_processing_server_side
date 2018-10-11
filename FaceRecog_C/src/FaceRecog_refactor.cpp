//============================================================================
// Name        : FaceRecog_refactor.cpp
// Author      : dehua lai
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>

#include "Face2.h"
#include "VideoProcessing.h"
#include "FileSystem.h"
#include <boost/filesystem.hpp>
#include <boost/property_tree/json_parser.hpp>
#include "score.h"
#include "FileCreatedRecorder.h"
#include "MatchResult.h"


using namespace std;
using namespace boost::filesystem;
using boost::property_tree::ptree;

int DEFINATE_MATCH = 1;
int DEFINATE_NOT_MATCH = 2;
int LIKELY_MATCH = 3;
int UNLIKELY_MATCH = 4;

string VERSION_NUMBER = "2.0.14(BASE)";



int finish_process(FileSystem* fileSystem, string message){

	fileSystem->writeJSON_Error(message);
	cout << fileSystem->getJSON() <<endl;
	FileCreatedRecorder::getInstance()->cleanUp();
	delete(fileSystem);
	exit(1);
	return 0;
}

vector<MatchResult*> matching(Face2* face, vector<ImgTpl*> videpTpl, vector<string> discTpl ){
	vector<MatchResult*> matchResult;
	for(vector<ImgTpl*>::size_type i = 0 ; i < videpTpl.size(); i++){
			for(vector<string>::size_type j = 0 ; j < discTpl.size(); j++){
				HNBuffer temp =  videpTpl.at(i)->getImageTemp();
				int score = face->match(&temp, discTpl[j] );
				MatchResult* rlt = new MatchResult(score, discTpl[j]);
				matchResult.insert(matchResult.end(), rlt);
			}
		}
	std::sort(matchResult.begin(), matchResult.end(),MatchResult::compare);
	return matchResult;
}

MatchResult* analysis(vector<MatchResult*> matchResult, FileSystem* fileSystem, bool isMatchingSelf){
	int average = 0 ;
	int sum1 = 1;
	int sum2 = 1;
	int max = 0 ;
	int min = 0;
	int num_middle_point = 0 ;
	bool pass_high_threshold = false;
	bool never_pass_low_threshold = true;

	MatchResult* rlt = NULL;

	int match_result = 0 ;
	for(unsigned i = 0 ; i<matchResult.size(); i++){
		sum1++;
		if(matchResult[i]->getScore() > 0 ){
			if(max==0){
				max = matchResult[i]->getScore();
			}
			min = matchResult[i]->getScore();
			sum2++;
			average += matchResult[i]->getScore();
		//	cout << i<< ":" << matchResult[i]->getScore() <<"==="<< matchResult[i]->getStep() <<endl;
		}
	}

	if(max>fileSystem->RECOG_SCORE_THRESHOLD_OTHER){
		match_result=DEFINATE_MATCH;
	}else if(max<fileSystem->RECOG_SCORE_THRESHOLD_SELF){
		match_result=DEFINATE_NOT_MATCH;
	}else{
		match_result=LIKELY_MATCH;
	}

	if(matchResult.size()>0){
		if(isMatchingSelf){
			if(match_result!=DEFINATE_NOT_MATCH){
				matchResult[0]->setIsMatch(true);
			}else{
				matchResult[0]->setIsMatch(false);
			}
		}else{
			if(match_result==DEFINATE_MATCH){
				matchResult[0]->setIsMatch(true);
			}else{
				matchResult[0]->setIsMatch(false);
			}
		}
		rlt = new MatchResult(matchResult[0]->getScore(), matchResult[0]->getPath());
		rlt->setStep(matchResult[0]->getStep());
		rlt->setIsMatch(matchResult[0]->getIsMatch());
		return rlt;
	}else{
		rlt = new MatchResult(0, fileSystem->getTemplateSelfPath());
		rlt->setIsMatch(false);
		return rlt;
	}

}


void writeJSON(FileSystem* fileSystem, MatchResult* matchResult, int whichTree /*2==self, 4==others*/){

	fileSystem->writeJSON(fileSystem->IS_MATCH, matchResult->getIsMatch()?"true":"false",whichTree);
	fileSystem->writeJSON(fileSystem->SCORE, matchResult->getScore(), whichTree);
	fileSystem->writeJSON(fileSystem->STEP,matchResult->getStep(), whichTree);
	fileSystem->writeJSON(fileSystem->PATH, matchResult->getPath(), whichTree);
	fileSystem->writeJSON(fileSystem->UNIQUE_VIDEO_ID, matchResult->getUniqueVideoId(), whichTree);
	fileSystem->writeJSON(fileSystem->BLUR_PREVIOUS_IMAGE_PATH, fileSystem->templatePath2imagePath(matchResult->getPath(), true), whichTree);
	fileSystem->writeJSON(fileSystem->UNBLUR_PREVIOUS_IMAGE_PATH, fileSystem->templatePath2imagePath(matchResult->getPath(), false), whichTree);
	if(whichTree==4){
		fileSystem->writeJSON("", "", 5);
	}
}

int main(int argc, char **argv) {
	FileSystem* fileSystem = new FileSystem();
	// check input arguments number
	if (argc != 2) {
		return finish_process(fileSystem, "Invalid number of input arguments. version "+VERSION_NUMBER);
	}

	// parse json
	if (fileSystem->parsingJSON(argv[1],0) < 0 ){
		return finish_process(fileSystem, fileSystem->getFileSystemException());
	}

	// parse xml
	if(fileSystem->parsingXML(fileSystem->getParameterConfigPath()) < 0){
		return finish_process(fileSystem, fileSystem->getFileSystemException());
	}
	// initial face parameters
	Face2 *face = new Face2();
	if(face->init(fileSystem->getParameterConfigPath().c_str()) != 0){
		delete(face);
		return finish_process(fileSystem, "exception caught in initial xml");
	}
	// check if NeuroTec license active
	if(!face->checkLicense()){
		delete(face);
		return finish_process(fileSystem, "Neurotec license is not actived");
	}



	VideoProcessing * vp = new VideoProcessing();
	vp->init(fileSystem, face);


	//  generate templates_video list from video path
	vector<ImgTpl*> template_video = vp->readVideo(fileSystem->getVideoPath().c_str());
	if(template_video.size()<=0){
		delete(face);
		delete(vp);
		return finish_process(fileSystem, "No Template can be generate from this video. It is either the video path incorrect, video file incorrent or Just the video is not good enough to generate a template");
	}


	// save current video face image int the current image path
//	cout << fileSystem->getUnblurCurrentSaveImagePath() << endl;
//	cout << fileSystem->getBlurCurrentSaveImagePath() << endl;
	template_video[0]->saveImage(fileSystem->getUnblurCurrentSaveImagePath(), fileSystem->getBlurCurrentSaveImagePath(), fileSystem->getBlurCroppedImagePath());


	// get self-template file list on disc
	vector<string> template_self = vp->readHardDisk2String(fileSystem->getTemplateSelfPath().c_str());


	if(template_self.size() <= 0){
		FileSystem::mode = fileSystem->ENROLL;
	}else{
		FileSystem::mode = fileSystem->VERIFY;
	}
	if(FileSystem::mode == fileSystem->ENROLL){
		string currentImagePath = fileSystem->getTemplateSelfPath();
		template_video[0]->saveImage(
				fileSystem->templatePath2imagePath(currentImagePath, false), // unblur
				fileSystem->templatePath2imagePath(currentImagePath, true),  // blur
				fileSystem->getBlurCroppedImagePath());
	}



	//match and analysis self list
	vector<MatchResult*> matchResults = matching(face, template_video, template_self);

	MatchResult* tempRlt = analysis(matchResults, fileSystem, true);
	writeJSON(fileSystem, tempRlt, 2);


	// if in enroll mode / or in verify mode, match score > RECOG_SCORE_THRESHOLD_SAVING_TEMPLATE: save tamplate
	if(FileSystem::mode == fileSystem->ENROLL ||
	  (FileSystem::mode == fileSystem->VERIFY && tempRlt->getScore()>= fileSystem->RECOG_SCORE_THRESHOLD_SAVING_TEMPLATE)){
		FileSystem::use_as_template = "true";
		for(unsigned i=0; i<template_video.size(); i++){
			template_video[i]->saveTemplate();
		}
	}


	delete(tempRlt);

	//clean self-matching result
	for(unsigned i = 0 ; i< matchResults.size(); i++){
		delete(matchResults.at(i));
	}




	// get other-template file list on disc
	vector<vector<string> > template_other = vp->readHardDisk2String(fileSystem->getTemplateOtherPath());
	// match and analysis other list
	for(unsigned i=0; i<template_other.size(); i++){
		vector<string> other = template_other[i];
		matchResults = matching(face, template_video, other);
		MatchResult* tempRlt2 = analysis(matchResults, fileSystem, false);
		writeJSON(fileSystem, tempRlt2, 4);
		//clean other-matching result
		for(unsigned i = 0 ; i< matchResults.size(); i++){
			delete(matchResults.at(i));
		}
		delete(tempRlt2);
	}



	fileSystem->writeJSON(fileSystem->RESULT, fileSystem->SUCCESS, 0);
	fileSystem->writeJSON(fileSystem->ERROR_MESSAGE, "no_error", 1);
	fileSystem->writeJSON(fileSystem->MODE, FileSystem::mode, 1);
	fileSystem->writeJSON(fileSystem->USE_AS_TEMPLATE, FileSystem::use_as_template, 1);
	fileSystem->writeJSON(fileSystem->BLUR_CURRENT_IMAGE_PATH, fileSystem->getBlurCurrentSaveImagePath(), 1);
	fileSystem->writeJSON(fileSystem->UNBLUR_CURRENT_IMAGE_PATH, fileSystem->getUnblurCurrentSaveImagePath(), 1);
	cout << fileSystem->getJSON() <<endl;



	face->releaseLicense();



	for(unsigned i=0; i<template_video.size(); i++){
		delete(template_video.at(i));
	}


	delete(fileSystem);
	delete(face);
	delete(vp);



//	FileCreatedRecorder::getInstance()->cleanUp();
	delete(FileCreatedRecorder::getInstance());
	return 0;
}
