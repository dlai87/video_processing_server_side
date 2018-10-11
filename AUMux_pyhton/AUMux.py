import json
import sys
import os
import subprocess
import functools
import xml.etree.ElementTree as ET

class MyJson(object):
	def __init__(self):
		super(MyJson, self).__init__()
		self.result = 'success'
		self.message = 'null'

	def parseInput(self, inputJson):
		ij = json.loads(inputJson)
		self.ffmpeg_path = ij['ffmpeg_path']
		self.ffprobe_path = ij['ffprobe_path']
		self.dummy_mp3_path = ij['dummy_mp3_path']
		self.input_videos = ij['video_path']
		self.audio_path = ij['audio_path']
		self.output_videos = ij['output_video_path']
		self.video_start_time = ij['video_start_time']
		self.video_end_time = ij['video_end_time']
		self.video_end_frame = ij['video_end_frame']
		self.audio_start_time = ij['audio_start_time']
		self.audio_end_time = ij['audio_end_time']
		self.audio_start_frame = ij['audio_start_frame']
		self.audio_end_frame = ij['audio_end_frame']
		if ".mp4" in self.input_videos[0] or ".mp4" in self.input_videos[1]:
			self.is_ios_device = True 
		else:
			self.is_ios_device = False
		

	def error(self, message):
		self.result='failure'
		self.message=message

	def parseOutput(self):
		print json.dumps({'result':self.result, 'message':self.message}, sort_keys=False, indent=4, separators=(',', ':'))


class Worker(object):
	def __init__(self, jObj):
		super(Worker, self).__init__()
		self.default_dummy_mp3_length = 15
		self.temp_sript_path = jObj.output_videos[0]+"_temp_script.sh"
		self.temp_video_path = jObj.output_videos[0]+"_temp_video.flv"
		print self.temp_sript_path
		print self.temp_video_path
		self.script = open(self.temp_sript_path, 'w+')
		self.jObj = jObj

	def excute(self):
		print "==1"
		#self.getVideoFileDuration()
		self.formatConvert(self.jObj.input_videos[0], self.jObj.output_videos[0], self.jObj.audio_path)
		print "==2"
		self.formatConvert(self.jObj.input_videos[1], self.jObj.output_videos[1], self.jObj.audio_path)
		self.script.close()
		print "==3"
		subprocess.call('chmod u+x ' + self.temp_sript_path, shell=True )
		print "==4"
		subprocess.call([self.temp_sript_path] , shell=True)

	def find_between(self, s, first, last ):
		try:
			start = s.index( first ) + len( first )
			end = s.index( last, start )
			return s[start:end]
		except Exception, e:
			return ''

	def getTimeInSec(self, string):
		time = 0
		substr = self.find_between(string, "Duration: ", ", start")
		times = substr.replace(':',' ').replace('.',' ').split()
		time = int(times[3])*10+int(times[2])*1000+(int)(times[1])*60*1000+(int)(times[0])*60*60*1000
		return time/1000

	def getVideoFileDuration(self):
		if not self.jObj.is_ios_device:
			if self.jObj.audio_path == "null":
				self.slowDownSpeed = 1
				self.audioOffset = 0
			else:
				result = subprocess.Popen([self.jObj.ffprobe_path, self.jObj.input_videos[0]], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
				string = ''
				for line in result.stdout.readlines():
					if "Duration" in line :
						string = line 

				originalDuration = self.getTimeInSec(string)
				if originalDuration > 0 :
					if self.jObj.video_end_time > self.jObj.video_start_time and self.jObj.video_end_frame: # if video information is valid
						if self.jObj.audio_path == 'null' or self.jObj.audio_end_frame - self.jObj.audio_start_frame <= 0:
							targetDuration = (self.jObj.video_end_time-self.jObj.video_start_time)/1000.0
						else:
							# define new duration
							targetDuration = ((self.jObj.audio_end_time-self.jObj.audio_start_time)/(self.jObj.audio_end_frame-self.jObj.audio_start_frame)*self.jObj.video_end_frame)/1000.0
					else:
						targetDuration = originalDuration
			#	print "targetDuration " + str(targetDuration) + " originalDuration " + str(originalDuration)
					if self.jObj.audio_start_frame != None and self.jObj.video_end_frame != None and self.jObj.video_end_frame > 0 :
						self.slowDownSpeed = targetDuration / originalDuration;
						self.audioOffset = targetDuration*self.jObj.audio_start_frame/self.jObj.video_end_frame
					else:
						self.slowDownSpeed = 1
						self.audioOffset = 0
				else:
					self.slowDownSpeed = 1
					self.audioOffset = 0
		else:
			self.slowDownSpeed = 1
			self.audioOffset = 0
		


	def deleteFile(self, filename):
		if filename!= '':
			self.script.write('chmod 777 ' + filename+'\n rm ' + filename+'\n')

	def muxAudioVideo(fun):
		@functools.wraps(fun)
		def decorator(self, input_video_path, output_video_path, input_audio_path):
		#	print input_video_path + 'muxAudioVideo '
			dummyMp3FilePath=''
			mergeMp3FilePath=''
			if input_audio_path != 'null':
				if not self.jObj.is_ios_device:
				#	print 'create ========================== mp3 file '
					dummyMp3FilePath = output_video_path + 'dummy.mp3'
					mergeMp3FilePath = output_video_path + 'merge.mp3'
					self.script.write(self.jObj.ffmpeg_path+' -i '+self.jObj.dummy_mp3_path+' -t '+str(self.audioOffset)+' -acodec copy ' + dummyMp3FilePath + '\n')
					self.script.write(self.jObj.ffmpeg_path+' -i '+dummyMp3FilePath+' -i '+self.jObj.audio_path+" -filter_complex '[0:0][1:0]concat=n=2:v=0:a=1[out]' -map '[out]' " + mergeMp3FilePath + '\n')
					input_audio_path = mergeMp3FilePath
			ret = fun(self, input_video_path, output_video_path, input_audio_path)
			self.deleteFile(dummyMp3FilePath)
			self.deleteFile(mergeMp3FilePath)
			return ret 
		return decorator

	def slowdownDecorator(fun):
		@functools.wraps(fun)
		def decorator(self, input_video_path, output_video_path, input_audio_path):
			slowDownInputPath=input_video_path
			#print input_video_path + 'muxAudioVideo '
			if self.slowDownSpeed!=1:
			#	print 'slow down ========================== ' +str(self.slowDownSpeed) + ' ' + str(self.audioOffset)
				setpts = '"setpts='+str(self.slowDownSpeed)+'*PTS"'
				slowDownInputPath = output_video_path+'temp.flv'
				self.script.write(self.jObj.ffmpeg_path+' -i '+input_video_path+' -filter:v '+setpts+' '+slowDownInputPath+'\n')
			ret = fun(self, slowDownInputPath, output_video_path, input_audio_path)
			if slowDownInputPath == input_video_path:
				slowDownInputPath = ''
			self.deleteFile(slowDownInputPath)
			return ret 
		return decorator


	@slowdownDecorator
	@muxAudioVideo
	def formatConvert(self, input_video_path, output_video_path , input_audio_path):
		
		flvFilePath = output_video_path + '.flv'
		webmFilePath = output_video_path + '.webm'
		mp4FilePath = output_video_path + '.mp4'

		self.writeConvertCommand(input_video_path, flvFilePath, input_audio_path)
		self.writeConvertCommand(input_video_path, webmFilePath, input_audio_path)
		self.writeConvertCommand(input_video_path, mp4FilePath, input_audio_path)
		

	def writeConvertCommand(self, input_video_path, output_video_path, input_audio_path):
		#print input_video_path[-4:]
		formatString = ' -vcodec copy -acodec copy '
		if output_video_path[-4:] == '.mp4':
			formatString = ' -vcodec h264 -acodec libvorbis '
		elif output_video_path[-5:] == '.webm':
			formatString = ' -vcodec libvpx -acodec libvorbis '

		if input_audio_path == 'null' or input_video_path[-4:]=='.mp4':
			input_audio_path = ''
		else:
			input_audio_path = ' -i ' + input_audio_path

		if input_video_path[-4:] == output_video_path[-4:]:
			self.script.write(self.jObj.ffmpeg_path+' -i '+input_video_path + input_audio_path + ' -vcodec copy -acodec copy ' + output_video_path+'\n')
		else:
			self.script.write(self.jObj.ffmpeg_path+' -i '+input_video_path + input_audio_path + formatString + output_video_path+'\n')


if __name__== '__main__':
    if len(sys.argv) != 2:
        print "Usage: python AUMux.py [INPUT_JSON] version 1.1; latest updated: 2016-07-11"
        exit(2)
    myJson = MyJson()
    try:
    	print "=====00"
    	myJson.parseInput(sys.argv[1])
    	print "=====01"
    	worker = Worker(myJson)
    	print "=====02"
    	worker.excute()
    	print "=====03"
    except Exception ,e:
    	myJson.error(str(e.message))
    finally:
    	#os.remove(worker.temp_sript_path)
    	myJson.parseOutput()

   


