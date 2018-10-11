/*
 * FileCreatedRecorder.cpp
 *
 *  Created on: Mar 27, 2014
 *      Author: dehua
 */

#include "FileCreatedRecorder.h"



FileCreatedRecorder::FileCreatedRecorder() {
	// TODO Auto-generated constructor stub

}

FileCreatedRecorder::~FileCreatedRecorder() {
	// TODO Auto-generated destructor stub
}

FileCreatedRecorder* FileCreatedRecorder::instance = new FileCreatedRecorder();

FileCreatedRecorder* FileCreatedRecorder::getInstance(){
	return instance;
}


void FileCreatedRecorder::addFilename(string filename){
	instance->fileList.insert(instance->fileList.end(), filename);
}

void FileCreatedRecorder::cleanUp(){
	for(int i =0; i < instance->fileList.size(); i++){
		if(exist(instance->fileList.at(i))){
			const char* filename = instance->fileList.at(i).c_str();
			remove(filename);
		}
	}
}

bool FileCreatedRecorder::exist(string name) {
	path p (name);
	if (exists( p )){
		return true;
	}else{
		return false;
	}

}

