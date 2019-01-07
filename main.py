'''
	This will:
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
'''


import youtube_dl
import os
from urllib.request import urlopen
#import autosub.__init__ as autosub 
#from google.cloud import speech_v1 #this was screwy and required a virtual environment ugh
import subprocess
import speech_recognition as sr
#from pydub import AudioSegment
import wave
import re 

#import pocketsphinx
#from pocketsphinx import AudioFile
#from pocketsphinx import get_model_path

#from wit import Wit
#wit_access_token = "ZQBXCERPIPEZQWASLJXQDANMIZL7BOO4"
#wit_client = Wit(wit_access_token)


#xml_data = urlopen("https://www.youtube.com/watch?v=TawI9iJIxBc&t=13704s").read()
#with open('vid.xml', 'w') as xml:
#	xml.write(str(xml_data))

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

def segment_wav(filename): #split up wav file into 15 minute segments in segmented subfolder
	#print(get_duration_minutes(folder_wav+filename))
	call = "ffmpeg -i "+folder_wav+filename+" -f segment -segment_time "+str(1*60)+" -c copy "+folder_seg+filename.replace(".wav","-%03d.wav")
	print(call)
	subprocess.call(call,shell=False)

def convert_mp4_to_wav():
	for file in os.listdir(folder_vids):
		print("Converting MP4 to wav: "+file)
		subprocess.call("ffmpeg -i \""+folder_vids+file+"\" -ab 160k -ac 2 -ar 44100 -vn \""+folder_wav+file.replace(".mp4",".wav")+"\"",shell=True)

#not used 
def get_duration_minutes(filename_with_path): #thanks to https://stackoverflow.com/questions/7833807/get-wav-file-length-or-duration/41617943
	process = subprocess.Popen(['ffmpeg',  '-i', filename_with_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdout, stderr = process.communicate()
	results = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout.decode(), re.DOTALL).groupdict()
	minutes = int(results['hours'])*60+int(results['minutes'])
	return(minutes)

def convert_wav_to_txt(): #still to be tested, wav files too big
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



###"GRAPHICAL" "USER" "INTERFACE" lul

#download_mp4_from_links()
#move_to_subfolders()
#convert_mp4_to_wav()

#segment_wav("test.wav")

#convert_wav_to_txt()



r = sr.Recognizer()
test_filename = "test-000.wav"
with sr.AudioFile(folder_seg+test_filename) as source:
	audio = r.record(source)
raw_sphinx = r.recognize_sphinx(audio)
with open(folder_txt+"test-000.txt", "a") as f:
	for line in raw_sphinx:
		f.write(line)
exit()

#errored out in c file
#model_path = get_model_path()
#decoder = pocketsphinx.Decoder(pocketsphinx.Decoder.default_config())
#wavFile = file(folder_seg+test_filename,'rb')
#wavFile.seek(44)
#decoder.decode_raw(wavFile)
#results = decoder.get_hyp()
#print(results)

exit()

resp = None
with open(folder_seg+test_filename,'rb') as wav:
	resp = wit_client.speech(wav, None, {'Content-Type':'audio/wav'})
print(str(resp))
#r = sr.Recognizer()
#with sr.AudioFile(folder_seg+test_filename) as test_source:
#	test_audio = r.record(test_source)
#print(r.recognize_wit(test_audio, key="ZQBXCERPIPEZQWASLJXQDANMIZL7BOO4"))
exit()
with open(folder_txt+"test.txt","w") as t:
	value = ""
	try:
		value = r.recognize_google(test_audio)
	except sr.RequestError as e:
		print("Error:   "+str(e))
	t.write(value)



#test_sphinx = r.recognize_sphinx(test_audio)
#print(test_sphinx)


