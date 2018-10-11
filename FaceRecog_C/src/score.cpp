/*
 * score.cpp
 *
 *  Created on: Oct 24, 2013
 *      Author: lei
 */

#include "score.h"

score::score() {
	// TODO Auto-generated constructor stub
	step = "";

}

score::~score() {
	// TODO Auto-generated destructor stub
}

int score::getScore() {
	return myScore;
}

void score::setScore(int myScore) {
	this->myScore = myScore;
}
/*
string score::getStepId()  {
	return stepId;
}

void score::setStepId( string stepId) {
	this->stepId = stepId;
}*/


string score::getStepId() {
	return step;
}
void score::setStepId(string step) {
	this->step = step;
}

void score::setSaveFolder(string saveFolder){
	this->saveFolder = saveFolder;
}

string score::getSaveFolder(){
	return saveFolder;
}

string score::getSaveBlurImageFolder(){

//	cout << "======1 " <<endl;
	string temp = refactorString(saveFolder, FileSystem::search_step_folder_name, FileSystem::blur_save_image_ext, true);
//	cout << "======1 111" <<endl;
	return refactorString(temp, FileSystem::search_template_folder_name, FileSystem::replace_folder_name,false);
}

string score::getSaveUnblurImageFolder(){
//	cout << "======2 " <<endl;
	string temp =  refactorString(saveFolder, FileSystem::search_step_folder_name, FileSystem::unblur_save_image_ext,true);
//	cout << "======2 222 " <<endl;
	return refactorString(temp, FileSystem::search_template_folder_name, FileSystem::replace_folder_name,false);
}

string score::refactorString(string originalString, string toBeReplace, string ReplaceString,  bool includeExternsion){
	string copyOriginal = originalString;
	int start_pos = copyOriginal.find(toBeReplace);
	if(includeExternsion){
		copyOriginal.replace(start_pos,ReplaceString.size(),ReplaceString);
	}else{
		copyOriginal.replace(start_pos,toBeReplace.size(),ReplaceString);
	}


	return copyOriginal;
}


