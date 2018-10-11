/*
 * MatchResult.cpp
 *
 *  Created on: Dec 23, 2014
 *      Author: lei
 */

#include "MatchResult.h"

MatchResult::MatchResult(int score, string path) {
	// TODO Auto-generated constructor stub
	this->score = score;
	this->path = path;
	std::size_t pos = path.find("-vid-");
	std::size_t pos_end = path.find(".tpl");
	if (pos != string::npos) {
		this->uniqueVideoId = path.substr(pos + 5, pos_end-pos-5);
	} else {
		this->uniqueVideoId = "";
	}
	pos = path.find("step_");
	if (pos != string::npos) {
		this->step = path.substr(pos + 5, 1);
	} else {
		this->step = "";
	}
}


MatchResult::~MatchResult() {
	// TODO Auto-generated destructor stub
}

void MatchResult::setIsMatch(bool isMatch){
	this->isMatch = isMatch;
}

bool MatchResult::getIsMatch(){
	return this->isMatch;
}


int MatchResult::getScore(){
	return this->score;
}

string MatchResult::getStep(){
	return this->step;
}

void MatchResult::setStep(string step){
	this->step = step;
}

string MatchResult::getPath(){
	return this->path;
}

string MatchResult::getUniqueVideoId(){
	return this->uniqueVideoId;
}

bool MatchResult::compare( MatchResult* obj1, MatchResult* obj2){
	return obj1->score > obj2->getScore();
}
