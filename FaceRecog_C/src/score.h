/*
 * score.h
 *
 *  Created on: Oct 24, 2013
 *      Author: lei
 */

#ifndef SCORE_H_
#define SCORE_H_

#include "Face2.h"
#include "FileSystem.h"

using namespace std;

class score {

private :
	int myScore;
	string saveFolder;
	string step;

	string refactorString(string originalString, string toBeReplace, string ReplaceString, bool includeExternsion);

	//string saveBlurImageFolder;
	//string saveUnblurImageFolder;
public:

	int getScore();
	void setScore(int myScore);

	void setStepId(string step);
	string getStepId();

	void setSaveFolder(string saveFolder);
	string getSaveFolder();

	string getSaveBlurImageFolder();
	string getSaveUnblurImageFolder();

	score();
	virtual ~score();


};

#endif /* SCORE_H_ */
