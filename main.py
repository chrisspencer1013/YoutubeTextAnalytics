'''
    From fresh ubuntu install do the following:
        sudo apt-get install python3 python3-all-dev build-essential swig git libpulse-dev
        sudo apt-get install libasound2-dev #solves error on build for pocketsphinx
        sudo apt-get install ffmpeg #for conversion, segmentation
        pip3 install youtube_dl
        pip3 install SpeechRecognition
        pip3 install pocketsphinx #might need to use an update statement instead
        pip3 install termcolor
        sudo apt-get install sox #for determining sampling rate of wav files

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
        https://cmusphinx.github.io/wiki/tutorialtuning/
        
    Things I've tried that didn't work:
        ->Google's API requires a virtual environment and was kinda screwy
        ->import autosub.__init__ as autosub 
        ->from pydub import AudioSegment (ffmpeg works fine, but I might test this later)
        ->some weird xml thing
        ->youtube-dl: download as wav (filetype not available)
        ->free wit translation - always seemed to time out, might have bad token
        ->pocketsphinx not through speech_recognition gives error in c stuff
        ->episode number was not populated from youtube-dl, hence the rename
'''


import youtube_dl
from termcolor import colored
import os
from urllib.request import urlopen
import subprocess
import speech_recognition as sr
#from pydub import AudioSegment
import wave
import re 
import pathlib

#import pocketsphinx
from pocketsphinx import AudioFile
from pocketsphinx import get_model_path
from pocketsphinx import get_data_path

folder_base = "/home/chris/Projects/YoutubeTextAnalytics/"
folder_vids = folder_base+"videos/"
folder_wav = folder_base+"wav/"
folder_seg = folder_wav+"segmented/"
folder_txt = folder_base+"text/"

pathlib.Path(folder_vids).mkdir(exist_ok=True) 
pathlib.Path(folder_wav).mkdir(exist_ok=True) 
pathlib.Path(folder_seg).mkdir(exist_ok=True) 
pathlib.Path(folder_txt).mkdir(exist_ok=True) 


class MyLogger(object):
    
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download_mp4_from_links(cleanup=0):
    print(colored('Downloading vids', 'green', attrs=['reverse']))
    #download everything in links file
    with open('links.txt','r') as links:
        for i, link in enumerate(links):
            print("Downloading video: {vid}".format(vid=link))
            args = {
                'verbose':True,
                'logger':MyLogger(),
                'subtitleslangs':'en',
                'skip_download':False,
                'format':'mp4',
                'outtmpl':'./videos/%(title)s-%(id)s.%(ext)s'
            }
            with youtube_dl.YoutubeDL(args) as youtube:
                youtube.download([link])


def segment_wav(full_filename): #split up wav file into 15 minute segments in segmented subfolder
    call = "ffmpeg -i \"" + full_filename + "\" -f segment -segment_time " + str(1*60) + " -c copy \"" + folder_seg+os.path.basename(full_filename).replace(".wav","-%03d.wav")+"\""
    print(colored('Segmenting wav file: '+full_filename, 'green'))
    #print(call)
    subprocess.call(call,shell=True)


def convert_mp4_to_wav(cleanup=0):
    for file in os.listdir(folder_vids):
        print("Converting MP4 to wav: " + file)
        subprocess.call("ffmpeg -i \"" + folder_vids+file + "\" -ab 160k -ac 1 -ar 16000 -vn \"" + folder_wav + file.replace(".mp4", ".wav") + "\"",shell=True)

def convert_wav_to_txt(cleanup=0): #still to be tested, wav files too big
    r = sr.Recognizer()
    for file in os.listdir(folder_wav):
        print("Converting wav to txt: "+file)
        segment_wav(folder_wav + file, cleanup)
        for segment in os.listdir(folder_seg):
            with sr.AudioFile(folder_seg+segment) as source:
                audio = r.record(source)
            raw_sphinx = r.recognize_sphinx(audio)
            with open(folder_txt+file.replace(".wav", ".txt"), "a") as f:
                for line in raw_sphinx:
                    f.write(line)
            #todo delete segments when done
            
def renamer():
    print(colored('Renaming mp4s', 'green', attrs=['reverse']))
    for file in [x for x in os.listdir(folder_vids) if x.endswith(".mp4")]:
        try:
            os.rename(folder_vids + file, folder_vids + "CriticalRole_S2E{}.mp4".format(re.search(r"Episode\s{1}(?P<e>\d+)", file, re.DOTALL)['e']))
        except TypeError as e:
            print(colored('Error renaming based on regex pattern', 'red', attrs=['reverse']))
            print(colored("\t"+str(e)+"\n",'red'))

def test_wav_to_txt(): #just so i can call it like the other steps (temp)
    r = sr.Recognizer()
    test_filename = "CriticalRole_S2E1-000.wav"
    with sr.AudioFile(folder_seg+test_filename) as source:
        audio = r.record(source)
    raw_sphinx = r.recognize_sphinx(audio)
    with open(folder_txt+"CriticalRole_S2E1-000.txt", "a") as f:
        for line in raw_sphinx:
            f.write(line)

def test_puresphinx():
    model_path = get_model_path()
    data_path = get_data_path()
    test_filename = "CriticalRole_S2E1-000.wav"
    config = {
        'verbose' : False,
        'audio_file' : os.path.join(folder_seg, test_filename),
        'buffer_size' : 2048,
        'hmm' : os.path.join('/home/chris/Projects/LanguageModels/wsj_all_sc.cd_semi_5000',''), #acoustic model
        #'hmm' : os.path.join(model_path, 'en-us'), #acoustic model
        'lm' : os.path.join(model_path, 'en-us.lm.bin'), #language model
        'dict' : os.path.join(model_path,'cmudict-en-us.dict')
    }
    audio = AudioFile(**config)
    for phrase in audio:
        print(phrase)
    



###"GRAPHICAL" "USER" "INTERFACE" lul

#download_mp4_from_links()
#renamer()
#convert_mp4_to_wav()
#segment_wav(folder_wav + "CriticalRole_S2E1.wav") 

#convert_wav_to_txt()
#test_wav_to_txt()
test_puresphinx()