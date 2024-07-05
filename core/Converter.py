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


#pathVideo is a list of the Path of the videos
#Converter from mp4 to mp3
def useConverter(pathVideo) :
    
    pathList = []

    for path in pathVideo:
      video = VideoFileClip(str(path))

      if not os.path.exists("Mp3"):
        os.makedirs("Mp3")

      pathMp3 = Path("Mp3") / (str(path).replace(".mp4", ".mp3"))

      pathList = pathList + [pathMp3]

      if not pathMp3.exists():

        #Converter
        video.audio.write_audiofile(pathMp3, logger=logger)

    #Call whisper for the transcription
    #Whisper.main(pathList)