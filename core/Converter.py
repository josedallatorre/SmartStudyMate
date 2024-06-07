#Converter from mp4 to mp3
import Whisper
from pathlib import Path
from moviepy.editor import *

#pathVideo is the position of the Video
#nameMp3 is the name that the mp3 have to be call
#Converter from mp4 to mp3
def useConverter(pathVideo, nameMp3) :
    video = VideoFileClip(pathVideo)

    pathMp3 = Path("Mp3") / (nameMp3 + ".mp3")
    #Converter
    video.audio.write_audiofile(pathMp3)

    #Call whisper for the transcription
    Whisper.useWhisper(str(pathMp3).replace("\\", "/" ), nameMp3 + ".pdf" )

#useConverter("Lezioni/Test.mp4" , "prova")