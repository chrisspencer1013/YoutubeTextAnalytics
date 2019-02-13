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
from datetime import datetime
#import pocketsphinx
from pocketsphinx import AudioFile
from pocketsphinx import get_model_path
from pocketsphinx import get_data_path


class MyLogger(object):
    
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class YoutubeTextAnalytics:

    def __init__(self, folder_base, links = None):

        #set up and create folders
        self.folder_base = folder_base
        self.folder_vids = self.folder_base + "videos/"
        self.folder_wav = self.folder_base + "wav/"
        self.folder_seg = self.folder_wav + "segmented/"
        self.folder_txt = self.folder_base + "text/"
        self.folder_analysis = self.folder_base + "analysis/"
        self.folder_logs = self.folder_base + "logs/"

        pathlib.Path(self.folder_vids).mkdir(exist_ok=True) 
        pathlib.Path(self.folder_wav).mkdir(exist_ok=True) 
        pathlib.Path(self.folder_seg).mkdir(exist_ok=True) 
        pathlib.Path(self.folder_txt).mkdir(exist_ok=True) 
        pathlib.Path(self.folder_analysis).mkdir(exist_ok=True) 
        pathlib.Path(self.folder_logs).mkdir(exist_ok=True)

        self.links = links

    
    def add_link(self, link):
        self.links.append(link)


    def logger(self, text):
        with open(self.folder_logs + 'YTA_{}.log'.format(datetime.now().strftime('%Y%m%d')), 'a' ) as log:
            log.write('{}: {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text))

    def full_run(self, cleanup = 0):
        self.download()
        self.convert_to_wav()
        self.speech_to_text()

    def download(self, cleanup = 0):
        print(colored('Downloading vids', 'green', attrs=['reverse']))
        #download everything in links file
        for link in self.links:
            self.logger("Downloading video: {vid}".format(vid=link))
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
        #self.rename_mp4()


    def segment_wav(self, full_filename): #split up wav file into segments in segmented subfolder
        call = "ffmpeg -i \"" + full_filename + "\" -f segment -segment_time " + str(1*60) + " -c copy \"" + self.folder_seg+os.path.basename(full_filename).replace(".wav","-%03d.wav")+"\""
        temp = 'Segmenting wav file: '+full_filename
        print(colored(temp, 'green'))
        self.logger(temp)
        subprocess.call(call,shell=True)


    def convert_to_wav(self, cleanup = 0):
        for file in os.listdir(self.folder_vids):
            self.logger("Converting MP4 to wav: " + file)
            subprocess.call("ffmpeg -i \"" + self.folder_vids+file + "\" -ab 160k -ac 1 -ar 16000 -vn \"" + self.folder_wav + file.replace(".mp4", ".wav") + "\"",shell=True)
            if cleanup:
                os.remove(self.folder_vids+file)


    def speech_to_text(self, cleanup = 0): 

        model_path = get_model_path()
        data_path = get_data_path()

        for file in os.listdir(self.folder_wav): #todo list propegation for only non folders

            self.segment_wav(self.folder_wav + file)

            segments_to_process = []
            for segment in os.listdir(self.folder_seg):
                segments_to_process.append(segment) #done because list dir isnt ordered

            for segment in sorted(segments_to_process):
                self.logger("Converting wav to txt: "+segment)
                config = {
                    'verbose' : False,
                    'audio_file' : os.path.join(self.folder_seg, segment),
                    'buffer_size' : 2048,
                    'hmm' : os.path.join('/home/chris/Projects/LanguageModels/wsj_all_sc.cd_semi_5000',''), #acoustic model
                    #'hmm' : os.path.join(model_path, 'en-us'), #acoustic model
                    'lm' : os.path.join(model_path, 'en-us.lm.bin'), #language model
                    'dict' : os.path.join(model_path,'cmudict-en-us.dict')
                }
                audio = AudioFile(**config)
                with open(self.folder_txt+file.replace(".wav", ".txt"), "w") as f:
                    for phrase in audio:
                        f.write(str(phrase))

            self.merge_text_files(cleanup)




    def merge_text_files(self, cleanup = 0):
        for text_file in os.listdir(self.folder_txt):
            with open(self.folder_txt+text_file, 'r') as text, open(self.folder_analysis + text_file.split("-")[0]+".txt", 'a') as cumulative:
                for line in text:
                    cumulative.write(line)
            if cleanup:
                os.remove(self.folder_txt+text_file)
 

    def rename_mp4(self): #only for the critical role stuff (bad oop design)
        print(colored('Renaming mp4s', 'green', attrs=['reverse']))
        for file in [x for x in os.listdir(self.folder_vids) if x.endswith(".mp4")]:
            try:
                os.rename(self.folder_vids + file, self.folder_vids + "CriticalRole_S2E{}.mp4".format(re.search(r"Episode\s{1}(?P<e>\d+)", file, re.DOTALL)['e']))
            except TypeError as e:
                print(colored('Error renaming based on regex pattern', 'red', attrs=['reverse']))
                print(colored("\t"+str(e)+"\n",'red'))
                self.logger(e)





    