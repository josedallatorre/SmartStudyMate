# Converter from mp4 to mp3
import Whisper
from pathlib import Path
from moviepy.editor import *
import os
from proglog import ProgressBarLogger
import time

# MyBarLogger print the percentage
class MyBarLogger(ProgressBarLogger):
    
    def bars_callback(self, bar, attr, value, old_value=None):     
        percentage = (value / self.bars[bar]['total']) * 100
        # Print the percentage of the conversion
        # print(percentage)

logger = MyBarLogger()


# pathVideo is a list of the Path of the videos
# courseName is the name of the course
# email is the email of the user
# Converter from mp4 to mp3
def useConverter(pathVideo, courseName, email):
    
    start_time_main = time.time()

    print("Start Conversion", flush=True)

    pathList = []

    for path in pathVideo:
        video = VideoFileClip(str(path))

        if not os.path.exists("Mp3"):
            os.makedirs("Mp3")

        pathMp3 = Path("Mp3") / str(path).split('/')[-1].replace(".mp4", ".mp3")

        pathList = pathList + [pathMp3]

        if not pathMp3.exists():
            # Converter
            video.audio.write_audiofile(pathMp3, logger=logger)

    print("Finish Conversion", flush=True)


    end_time_main = time.time()
    total_time_converter = end_time_main - start_time_main

    if not os.path.exists("Generate/Time"):
        os.makedirs("Generate/Time")   

    nameTimeFile = Path("Generate/Time") / str("Converter" + courseName + ".txt")
    with open(nameTimeFile, "w") as f:
        f.write(f"Total time taken: {total_time_converter} seconds.")

    
    # Rinomina la variabile 'time' per evitare conflitti con il modulo time

    # Call Whisper for the transcription
    Whisper.main(pathList, courseName, email)