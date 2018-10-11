/*
 * ImgTpl.h
 *
 *  Created on: Dec 23, 2014
 *      Author: dehua
 */

#ifndef IMGTPL_H_
#define IMGTPL_H_


#include "opencv/cv.h"
#include "opencv/highgui.h"
#include "Face2.h"
#include "FileSystem.h"
#include <NCore.h>
#include <sys/time.h>

#include <NImages.h>
#include <NLExtractor.h>
#include <NMatcher.h>
#include <NTemplate.h>
#include <NLicensing.h>
#include <NTypes.h>
#include <TutorialUtils.h>
#include <NError.h>

#include <boost/filesystem.hpp>



using namespace std;
using namespace boost::filesystem;



class ImgTpl {
private:
	FileSystem * fileSystem;
	Face2* face;
	IplImage* iplImage;
	string saveFolder;
	static int currentVideoSaveTemplate;

	int generateTemplate();
	HNBuffer imageTemp;
	IplImage* blurImgPatch(IplImage* inputImg);
	int countFolderContains(string filepath, string externsion);
public:

	bool processOneImage(IplImage* iplImage);


	void setSaveFolder(string saveFolder);
	int saveTemplate();
	IplImage* getIplImage();
	HNBuffer getImageTemp();
//	void setIplImage(IplImage* iplImage);
	bool saveImage(string saveUnblurImagePath, string saveBlurImagePath, string blurred_cropped_img_path);


	ImgTpl(FileSystem * fileSystem, Face2* face);
	virtual ~ImgTpl();

};

#endif /* IMGTPL_H_ */
