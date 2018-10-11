/*
 * Face2.h
 *
 *  Created on: Oct 2, 2013
 *      Author: dehua
 */

#ifndef FACE2_H_
#define FACE2_H_

#include <NCore.h>
#include <NImages.h>
#include <NLExtractor.h>
#include <NMatcher.h>
#include <NTemplate.h>
#include <NLicensing.h>
#include <NTypes.h>
#include <TutorialUtils.h>
#include <NError.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <boost/filesystem.hpp>

using namespace std;

class Face2 {
private:
	int NO_ERROR;
	int ERROR_NLE_CREATE;
	int ERROR_SETTING;
	int ERROR_IMAGE_CREATE_FROM_FILE_EX;
	int ERROR_IMAGE_TO_GRAY;
	int ERROR_EXTRACT_FACE;
	int ERROR_TEMPLATE_CREATE;
	int ERROR_IDENTIFY_START;
	int ERROR_IDENTIFY_NEXT;

	NDouble face_confidence_threshold;
	NInt min_iod;
	NInt max_iod;
	NByte face_quality_threshold;
	NShort max_roll_angle;
	NShort max_yaw_angle;
	NBoolean detect_all_feature_points;
	NBoolean detect_base_feature_points;
	NBoolean favor_LARGEST_FACE;
	string license_components;
	string server_url;
	string port;
	const NChar * components;
	NResult internalSetParameters(HNLExtractor * extract,
			NleTemplateSize templSize);
	int readTplFromDisc(string filename, HNBuffer* imageTemp);

public:

	int init(const char* xmlPath);
//	HNGrayscaleImage* convert_image(IplImage *iplImage);

	bool checkLicense();
	bool releaseLicense();
	int extractTemplate(IplImage *iplImage, HNBuffer *output);
	int match(HNBuffer *probeTemplate, HNBuffer * galleryTemplates);
	int match(HNBuffer *videoTpl, string  discTpl);

	Face2();
	virtual ~Face2();
};

#endif /* FACE2_H_ */
