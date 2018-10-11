/*
 * FileCreatedRecorder.h
 *
 *  Created on: Mar 27, 2014
 *      Author: dehua
 */

#ifndef FILECREATEDRECORDER_H_
#define FILECREATEDRECORDER_H_

#include <iostream>
#include <string>
#include <stdio.h>
#include <vector>
#include <boost/filesystem.hpp>

using namespace std;
using namespace boost::filesystem;


class FileCreatedRecorder {
public:
	std::vector<string> fileList;
	static FileCreatedRecorder* getInstance();
	void addFilename(string filename);
	void cleanUp();
	virtual ~FileCreatedRecorder();


private:
	bool exist(string name);
	FileCreatedRecorder();
	FileCreatedRecorder(const FileCreatedRecorder&);
	FileCreatedRecorder& operator=(const FileCreatedRecorder&);

	static FileCreatedRecorder* instance;
};

#endif /* FILECREATEDRECORDER_H_ */
