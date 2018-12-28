'''
	This will:
	 	download youtube vids, 
	 	convert to wav, 
	 	segment them to smaller pieces, 
	 	convert to text,
	 	do some fancy text analytics

	 Helpful links:
	 	https://github.com/Uberi/speech_recognition
	 	https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py
		https://pypi.org/project/SpeechRecognition/
'''


import youtube_dl
import os
from urllib.request import urlopen
#import autosub.__init__ as autosub 
#from google.cloud import speech_v1 #this was screwy and required a virtual environment ugh
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
import wave
import re 

#xml_data = urlopen("https://www.youtube.com/watch?v=TawI9iJIxBc&t=13704s").read()
#with open('vid.xml', 'w') as xml:
#	xml.write(str(xml_data))

folder_base = "D:/Projects/Youtube Text Analytics/"
folder_vids = folder_base+"videos/"
folder_wav = folder_base+"wav/"
folder_txt = folder_base+"text/"

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def download_mp4_from_links():
	args = {
		'verbose':True,
		'logger':MyLogger(),
		'subtitleslangs':'en',
		'skip_download':False
	}
	#download everything in links file
	with open('links.txt','r') as links:
		for link in links:
			print("Downloading: "+link)
			with youtube_dl.YoutubeDL(args) as youtube:
				youtube.download([link])

	#skip a step by downloading as sound file -> cant seem to get this working as intended
	#args = {
	#	'verbose':True,
	#	'logger':MyLogger(),
	#	'subtitleslangs':'en',
	#	'skip_download':False,
	#	'extract_audio':True,
	#	'audio-format':"wav"
	#}
	#with open('links.txt','r') as links:
	#	for link in links:
	#		print("Downloading: "+link)
	#		with youtube_dl.YoutubeDL(args) as youtube:
	#			youtube.download([link])
	#exit()

#move to subfolder for ease of use
def move_to_subfolders():
	for file in [x for x in os.listdir(folder_base) if x.endswith(".mp4")]:
		os.rename(file, folder_vids+file)
	for file in [x for x in os.listdir(folder_base) if x.endswith(".wav")]:
		os.rename(file, folder_wav+file)

def convert_mp4_to_wav():
	for file in os.listdir(folder_vids):
		print("Converting MP4 to wav: "+file)
		subprocess.call("G:/Programs/ffmpeg/bin/ffmpeg -i \""+folder_vids+file+"\" -ab 160k -ac 2 -ar 44100 -vn \""+folder_wav+file.replace(".mp4",".wav")+"\"",shell=True)

def convert_wav_to_txt(): #still to be tested, wav files too big
	r = sr.Recognizer()
	for file in os.listdir(folder_wav):
		print("Converting wav to txt: "+file)
		segment_wav(file)
		exit()
		with sr.AudioFile(folder_wav+file) as source:
			audio = r.record(source)
		raw_sphinx = r.recognize_sphinx(audio)
		exit()
		with open(folder_txt+file.replace(".wav",".txt"), "w") as f:
			for line in raw_sphinx:
				f.write(line)

#TODO: segment the wav files, they are too big as it stands lul

#takes filename, splits up wav to smaller ones, returns list of filenames
def segment_wav(filename):
	minutes = get_duration_minutes(folder_wav+filename) 
	print(minutes)

#example from https://stackoverflow.com/questions/37999150/python-how-to-split-a-wav-file-into-multiple-wav-files:
 #t1 = t1 * 1000 #Works in milliseconds
 #t2 = t2 * 1000
 #newAudio = AudioSegment.from_wav("oldSong.wav")
 #newAudio = newAudio[t1:t2]
 #newAudio.export('newSong.wav', format="wav") #Exports to a wav file in the current path.

def get_duration_minutes(filename_with_path): #thanks to https://stackoverflow.com/questions/7833807/get-wav-file-length-or-duration/41617943
	process = subprocess.Popen(['ffmpeg',  '-i', filename_with_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdout, stderr = process.communicate()
	results = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout.decode(), re.DOTALL).groupdict()
	minutes = int(results['hours'])*60+int(results['minutes'])
	return(minutes)


###"GRAPHICAL" "USER" "INTERFACE" lul

#download_mp4_from_links()
#move_to_subfolders()
#convert_mp4_to_wav()
convert_wav_to_txt()

