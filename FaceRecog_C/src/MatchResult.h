/*
 * MatchResult.h
 *
 *  Created on: Dec 23, 2014
 *      Author: lei
 */

#ifndef MATCHRESULT_H_
#define MATCHRESULT_H_
#include "FileSystem.h"
using namespace std;


class MatchResult {
private:
	int score;
	string step;
	string path;
	string uniqueVideoId;
	bool isMatch;
public:
	void setIsMatch(bool isMatch);
	bool getIsMatch();
	void setStep(string step);
	int getScore();
	string getStep();
	string getPath();
	string getUniqueVideoId();
	MatchResult(int score, string path);
	static bool compare( MatchResult* obj1, MatchResult* obj2);
	virtual ~MatchResult();
};

#endif /* MATCHRESULT_H_ */
