/*
 * VideoProcessing.h
 *
 *  Created on: Oct 3, 2013
 *      Author: lei
 */

#ifndef VIDEOPROCESSING_H_
#define VIDEOPROCESSING_H_


#include "Face2.h"
#include "opencv/cv.h"
#include "opencv/highgui.h"
#include "ImgTpl.h"

#include <NCore.h>
#include <NImages.h>
#include <NLExtractor.h>
#include <NMatcher.h>
#include <NTemplate.h>
#include <NLicensing.h>
#include <NTypes.h>
#include "FileSystem.h"

#include <boost/filesystem.hpp>
#include <boost/property_tree/json_parser.hpp>



using namespace std;
using namespace boost::filesystem;
using boost::property_tree::ptree;

class VideoProcessing {

private :

	FileSystem * fileSystem;
	const char* input_video_path;
	const char* templates_path;
	vector<string> templates_path_list;
	vector<int> step_id_vec;
	vector<string> step_folder_name;
	vector<int> frame_id_vec;
	vector<int> match_score_vec;
	string fileSystemErrorMessage;

	Face2* face;


	//functions

	void createStepsBaseOnVideoInfo();
	void createTemplateFoldersBaseOnSteps();
	int checkPath(const char* path);
//	vector<path> countFolderContains(const char* filepath, const char* externsion);


public:
	// initialize all the parameters and settings with json files, which store video information
	// must be called before using the class
	int init(FileSystem *fileSystem, Face2* face);
	int run(int mode);
	void printAll();
	vector<ImgTpl*> readVideo(const char* videoPath);
//	vector<ImageTpl*> readHardDisk(const char* rootPath);
//	vector<vector<ImageTpl*> > readHardDisk(vector<string> otherTemplatePath);

	vector<string> readHardDisk2String(const char* rootPath);
	vector<vector<string> > readHardDisk2String(vector<string> otherTemplatePath);

	VideoProcessing();
	virtual ~VideoProcessing();
};

#endif /* VIDEOPROCESSING_H_ */
