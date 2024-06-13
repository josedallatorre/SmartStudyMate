#Converter from mp4 to mp3
import Whisper
from pathlib import Path
from moviepy.editor import *
import os
from proglog import ProgressBarLogger

#MyBarLogger print the percentage
class MyBarLogger(ProgressBarLogger):
    
    def bars_callback(self, bar, attr, value,old_value=None):     
        percentage = (value / self.bars[bar]['total']) * 100
        #Print the percentage of the convertion
        print(percentage)

logger = MyBarLogger()


#pathVideo is the position of the Video
#nameMp3 is the name that the mp3 have to be call
#Converter from mp4 to mp3
def useConverter(pathVideo, nameMp3) :
    video = VideoFileClip(pathVideo)

    if not os.path.exists("Mp3"):
      os.makedirs("Mp3")
    pathMp3 = Path("Mp3") / (nameMp3 + ".mp3")
    #Converter
    video.audio.write_audiofile(pathMp3, logger=logger)

    pathPdf = Path("Pdf") / nameMp3 + ".pdf"

    #Call whisper for the transcription
    Whisper.useWhisper(str(pathMp3).replace("\\", "/" ), pathPdf )

#useConverter("Test.mp4" , "prova")