'''
	From fresh ubuntu install do the following:
		sudo apt-get install python3 python3-all-dev build-essential swig git libpulse-dev
		sudo apt-get install libasound2-dev #solves error on build for pocketsphinx
		sudo apt-get install ffmpeg #for conversion, segmentation
		pip3 install youtube_dl
		pip3 install SpeechRecognition
		pip3 install pocketsphinx #might need to use an update statement instead

	This script will:
	 	download youtube vids, 
	 	convert to wav, 
	 	segment them to smaller pieces, 
	 	convert to text,
	 	do some fancy text analytics

	 Helpful links:
	 	https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py
	 	https://github.com/Uberi/speech_recognition
	 	https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py
		https://pypi.org/project/SpeechRecognition/
		https://github.com/rg3/youtube-dl/blob/master/README.md#output-template
		
	Things I've tried that didn't work:
		->Google's API requires a virtual environment and was kinda screwy
		->import autosub.__init__ as autosub 
		->from pydub import AudioSegment (ffmpeg works fine, but I might test this later)
		->some weird xml thing
		->youtube-dl: download as wav (filetype not available)
		->free wit translation - always seemed to time out, might have bad token
		->pocketsphinx not through speech_recognition gives error in c stuff
'''


import youtube_dl
import os
from urllib.request import urlopen
import subprocess
import speech_recognition as sr
#from pydub import AudioSegment
import wave
import re 

#import pocketsphinx
#from pocketsphinx import AudioFile
#from pocketsphinx import get_model_path

folder_base = "/home/pythondevbox/Projects/YoutubeTextAnalytics/"
folder_vids = folder_base+"videos/"
folder_wav = folder_base+"wav/"
folder_seg = folder_wav+"segmented/"
folder_txt = folder_base+"text/"


class MyLogger(object):
	
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download_mp4_from_links(cleanup=0):

	#download everything in links file
	with open('links.txt','r') as links:
		for i, link in enumerate(links):
			print("Downloading video number {num}: {vid}".format(num=str(i+1),vid=link))
			args = {
				'verbose':True,
				'logger':MyLogger(),
				'subtitleslangs':'en',
				'skip_download':False,
				'format':'mp4',
				'outtmpl':'./videos/CriticalRole_S2E{}.%(ext)s'.format(str(i+1)) #sloppy, but it will work (episode number wasn't populated)
			}
			with youtube_dl.YoutubeDL(args) as youtube:
				youtube.download([link])


def segment_wav(filename,cleanup=0): #split up wav file into 15 minute segments in segmented subfolder
	call = "ffmpeg -i '"+folder_wav+filename+"' -f segment -segment_time "+str(1*60)+" -c copy '"+folder_seg+filename.replace(".wav","-%03d.wav")+"'"
	print(call)
	subprocess.call(call,shell=False)

def convert_mp4_to_wav(cleanup=0):
	for file in os.listdir(folder_vids):
		print("Converting MP4 to wav: "+file)
		subprocess.call("ffmpeg -i \""+folder_vids+file+"\" -ab 160k -ac 2 -ar 44100 -vn \""+folder_wav+file.replace(".mp4",".wav")+"\"",shell=True)

def convert_wav_to_txt(cleanup=0): #still to be tested, wav files too big
	r = sr.Recognizer()
	for file in os.listdir(folder_wav):
		print("Converting wav to txt: "+file)
		segment_wav(file)
		for segment in os.listdir(folder_seg):
			with sr.AudioFile(folder_seg+segment) as source:
				audio = r.record(source)
			raw_sphinx = r.recognize_sphinx(audio)
			with open(folder_txt+file.replace(".wav",".txt"), "a") as f:
				for line in raw_sphinx:
					f.write(line)
			#todo delete segments when done
			
def renamer(): #untested
    for file in [x for x in os.listdir(folder_vids) if x.endswith(".mp4")]:
        os.rename(file, "CriticalRole_S2E{}.mp4".format(re.search(r"Episode\s{1}(?P<e>\d+)", file, re.DOTALL)['e']))


###"GRAPHICAL" "USER" "INTERFACE" lul

download_mp4_from_links()
renamer()
#convert_mp4_to_wav()

#segment_wav("test.wav") #review this, it wasnt workin

#convert_wav_to_txt()
exit()


r = sr.Recognizer()
test_filename = "test-000.wav"
with sr.AudioFile(folder_seg+test_filename) as source:
	audio = r.record(source)
raw_sphinx = r.recognize_sphinx(audio)
with open(folder_txt+"test-000.txt", "a") as f:
	for line in raw_sphinx:
		f.write(line)
exit()
