/*
 * Face2.cpp
 *
 *  Created on: Oct 2, 2013
 *      Author: dehua
 */


#include "Face2.h"


#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/filesystem.hpp>

using namespace boost::filesystem;
using boost::property_tree::ptree;
using namespace boost::property_tree;

Face2::Face2() {
	// TODO Auto-generated constructor stub

	NO_ERROR = 0;
	ERROR_NLE_CREATE = -1;
	ERROR_SETTING = -2;
	ERROR_IMAGE_CREATE_FROM_FILE_EX = -3;
	ERROR_IMAGE_TO_GRAY = -4;
	ERROR_EXTRACT_FACE = -5;
	ERROR_TEMPLATE_CREATE = -6;
	ERROR_IDENTIFY_START = -7;
	ERROR_IDENTIFY_NEXT = -8;

}

Face2::~Face2() {
	// TODO Auto-generated destructor stub
}


int Face2::init(const char* xmlPath){
	ptree tree;
	try {
		read_xml(xmlPath, tree);
		face_confidence_threshold = tree.get<NDouble>(
				"parameter.face_confidence_threshold");
		min_iod = tree.get<NInt>("parameter.min_iod");
		max_iod = tree.get<NInt>("parameter.max_iod");
		;
		face_quality_threshold = tree.get<NByte>(
				"parameter.face_quality_threshold");
		max_roll_angle = tree.get<NShort>("parameter.max_roll_angle");
		max_yaw_angle = tree.get<NShort>("parameter.max_yaw_angle");
		detect_all_feature_points = tree.get<NBoolean>(
				"parameter.detect_all_feature_points");
		detect_base_feature_points = tree.get<NBoolean>(
				"parameter.detect_base_feature_points");
	//	favor_LARGEST_FACE = true;
		license_components = tree.get<string>("general.license_components");
		server_url = tree.get<string>("general.server_url");
		port = tree.get<string>("general.port");
	//	cout << "min_iod " << min_iod <<endl;
	} catch (exception const&e) {
	//	cout << "exception caught in reading parameter config xml file : "<<e.what() <<endl;
		return -1;
	}
	return 0;

}


bool Face2::checkLicense() {
	NResult result = N_OK;
	NBool available = NFalse;

	components = { N_T(license_components.c_str()) };

	//cout << "NLicenseObtainComponents" << components <<endl;
	// check the license first
	result = NLicenseObtainComponents(N_T(server_url.c_str()), N_T(port.c_str()), components,
			&available);
	if (NFailed(result)) {
		return false;
	}
	if (!available) {
//		cout << "Licenses for %s not available\n" << components << endl;
		result = N_E_FAILED;
		return false;
	}

	return true;
}

bool Face2::releaseLicense(){
	//cout << "NLicenseReleaseComponents" << components <<endl;
	NResult result = NLicenseReleaseComponents(components);
	if(NFailed(result)){
		return false;
	}
	return true;
}



NResult Face2::internalSetParameters(HNLExtractor * extract,
		NleTemplateSize templSize) {
	/* setting parameters of extractor */

	NUShort template_size = 128;
	NObjectSetParameterEx(*extract, NLEP_FACE_CONFIDENCE_THRESHOLD,
			N_TYPE_DOUBLE, &face_confidence_threshold,
			sizeof(face_confidence_threshold));
	NObjectSetParameterEx(*extract, NLEP_MIN_IOD, N_TYPE_INT, &min_iod,
			sizeof(min_iod));
	NObjectSetParameterEx(*extract, NLEP_TEMPLATE_SIZE, N_TYPE_SHORT, &template_size,
				sizeof(template_size));
	NObjectSetParameterEx(*extract, NLEP_MAX_IOD, N_TYPE_INT, &max_iod,
			sizeof(max_iod));
	NObjectSetParameterEx(*extract, NLEP_FACE_QUALITY_THRESHOLD, N_TYPE_BYTE,
			&face_quality_threshold, sizeof(face_quality_threshold));
	NObjectSetParameterEx(*extract, NLEP_MAX_ROLL_ANGLE_DEVIATION, N_TYPE_SHORT,
			&max_roll_angle, sizeof(max_roll_angle));
	NObjectSetParameterEx(*extract, NLEP_MAX_YAW_ANGLE_DEVIATION, N_TYPE_SHORT,
			&max_yaw_angle, sizeof(max_yaw_angle));
	NObjectSetParameterEx(*extract, NLEP_DETECT_ALL_FEATURE_POINTS, N_TYPE_BOOL,
			&detect_all_feature_points, sizeof(detect_all_feature_points));
	NObjectSetParameterEx(*extract, NLEP_DETECT_BASE_FEATURE_POINTS, N_TYPE_BOOL,
				&detect_base_feature_points, sizeof(detect_base_feature_points));
//	NObjectSetParameterEx(*extract, NLEP_FAVOR_LARGEST_FACE , N_TYPE_BOOL,	&favor_LARGEST_FACE, sizeof(favor_LARGEST_FACE));
	// set template size
	return NObjectSetParameterEx(*extract, NLEP_TEMPLATE_SIZE, N_TYPE_INT,
			&templSize, sizeof(templSize));
}


int Face2::extractTemplate(IplImage *iplImage,  HNBuffer *output) {




	HNImage image;
	NleDetectionDetails details;
	NleExtractionStatus extrStatus;
	HNLTemplate templ;
	HNLExtractor extractor;
	NleTemplateSize templSize = nletsLarge;
	NResult result;

	HNGrayscaleImage grayscale;


	result = NleCreate(&extractor);
	if (NFailed(result)) {
		NObjectFree(extractor);
		return ERROR_NLE_CREATE;
	}

	result = internalSetParameters(&extractor, templSize);
	if (NFailed(result)) {
		NObjectFree(extractor);
		return ERROR_SETTING;
	}

	result = NImageCreateWrapper(NPF_RGB_8U, iplImage->width, iplImage->height,
			iplImage->nChannels * iplImage->width, 0, 0, iplImage->imageData, 0,
			&image);
//	free(&iplImage);
	if (NFailed(result)) {
		NObjectFree(image);
		NObjectFree(extractor);
		return -1;
	}

	result = NImageToGrayscale(image, &grayscale);
	NObjectFree(image);
	if (NFailed(result)) {
		NObjectFree(extractor);
		return ERROR_IMAGE_TO_GRAY;
	}

	result = NleExtract(extractor, grayscale, &details, &extrStatus, &templ);



	NObjectFree(grayscale);
	NObjectFree(extractor);
	if (NFailed(result)) {
		NObjectFree(templ);
		return ERROR_EXTRACT_FACE;
	}

	if (extrStatus != nleesTemplateCreated) {
		NObjectFree(templ);
	//	printf("template extraction failed (extraction status = %d)\n", extrStatus);
		return ERROR_TEMPLATE_CREATE;
	}


//	cout << templ <<endl;
	// save template to buffer
	result = NObjectSaveToMemoryN(templ, 0, output);

	NObjectFree(templ);



	return NO_ERROR;

}


int Face2::readTplFromDisc(string filename, HNBuffer* imageTemp ){

	if (!ReadAllBytesN(filename.c_str(), imageTemp)) {
		NObjectFree(*imageTemp);
		if(imageTemp!=NULL){
			free(imageTemp);
			imageTemp=NULL;
		}

		return -1;
	}
	return 0;
}

int Face2::match(HNBuffer *videoTpl, string  discTplPath){

	HNBuffer* discTpl = (HNBuffer*) malloc( sizeof(HNBuffer));
	int result = readTplFromDisc(discTplPath, discTpl);


	if(result!=0){
	//	cout << "cannot read tpl from disc" << discTplPath << endl;
		NObjectFree(*discTpl);
		if(discTpl!=NULL){
			free(discTpl);
			discTpl= NULL;
		}

		return -1;
	}
	int score =  match(videoTpl, discTpl);

	NObjectFree(*discTpl);
	if(discTpl!=NULL){
		free(discTpl);
		discTpl= NULL;
	}
	return score;
}

int Face2::match(HNBuffer *probeTemplate, HNBuffer * galleryTemplates) {

	if (probeTemplate == NULL || galleryTemplates == NULL) {
//		cout << "====1" << probeTemplate <<"==" << galleryTemplates <<endl;
		return -1;
	}

	HNMatcher matcher = NULL;
	NResult result = N_OK;
	HNMatchingDetails hMatchingDetails = NULL;
	NInt score = -1;
	NDouble sscore = -1;

	// create a matcher

	result = NMCreate(&matcher);
	if (NFailed(result)) {
		NObjectFree(matcher);
		NObjectFree(hMatchingDetails);
	//	cout << "====2"<<endl;
		return ERROR_NLE_CREATE;
	}


	NSizeType template_size = 128;
	// perform verification
		result = NMVerifyExN(matcher, *galleryTemplates,*probeTemplate, &hMatchingDetails, &score);
	//	result = NlsmVerify(matcher, *probeTemplate ,template_size, *galleryTemplates, template_size, &hMatchingDetails, &sscore);
		if (NFailed(result))
		{
			return result;
		}
	//	cout << "verify score:" << score <<endl;

		NObjectFree(matcher);
		NObjectFree(hMatchingDetails);

		return score;


/*
	// identify face from the image by comparing to each template from arguments

	result = NMIdentifyStartExN(matcher, *probeTemplate, &hMatchingDetails);
	if (NFailed(result)) {
		NObjectFree(matcher);
		NObjectFree(hMatchingDetails);
	//	cout << "====3"<<endl;
		return ERROR_IDENTIFY_START;
	}

	result = NMIdentifyNextExN(matcher, *galleryTemplates, hMatchingDetails,
			&score);
	if (NFailed(result)) {
		NObjectFree(matcher);
		NObjectFree(hMatchingDetails);
	//	cout << "====4"<<endl;
		return ERROR_IDENTIFY_NEXT;
	}



	NObjectFree(matcher);
	NObjectFree(hMatchingDetails);

	return score;

*/
}

