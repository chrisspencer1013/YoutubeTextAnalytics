import youtube_dl
import os
from urllib.request import urlopen
#import autosub.__init__ as autosub 
#from google.cloud import speech_v1 #this was screwy and required a virtual environment ugh
import subprocess
import speech_recognition as sr
from pydub import AudioSegment

#xml_data = urlopen("https://www.youtube.com/watch?v=TawI9iJIxBc&t=13704s").read()
#with open('vid.xml', 'w') as xml:
#	xml.write(str(xml_data))

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

args = {
	'verbose':True,
	'logger':MyLogger(),
	'subtitleslangs':'en',
	'skip_download':False
}

#download everything in links file
#with open('links.txt','r') as links:
#	for link in links:
#		print("Downloading: "+link)
#		with youtube_dl.YoutubeDL(args) as youtube:
#			youtube.download([link])

#move to subfolder for ease of use
#for file in [x for x in os.listdir("D:/Projects/Youtube Text Analytics/") if x.endswith(".mp4")]:
#	os.rename(file, "D:/Projects/Youtube Text Analytics/Videos/"+file)

# doesn't seem like this is working...
folder_base = "D:/Projects/Youtube Text Analytics/"
folder_vids = folder_base+"videos/"
folder_wav = folder_base+"wav/"
folder_txt = folder_base+"text/"

r = sr.Recognizer()
#client = speech_v1.SpeechClient()
def convert_mp4_to_wav():
	for file in os.listdir(folder_vids):
		subprocess.call("G:/Programs/ffmpeg/bin/ffmpeg -i \""+folder_vids+file+"\" -ab 160k -ac 2 -ar 44100 -vn \""+folder_wav+file.replace(".mp4",".wav")+"\"",shell=True)

def convert_wav_to_txt():
	for file in os.listdir(folder_wav):
		print(folder_wav+file)
		with sr.AudioFile(folder_wav+file) as source:
			audio = r.record(source)
		raw_sphinx = r.recognize_sphinx(audio)
		exit()
		with open(folder_txt+file.replace(".wav",".txt"), "w") as f:
			for line in raw_sphinx:
				f.write(line)



#convert_mp4_to_wav()
convert_wav_to_txt()