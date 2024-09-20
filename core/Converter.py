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

# sum the duration of the videos
def sumDurationVideo(video_paths):
    total_seconds = 0
    
    for video_path in video_paths:
        clip = VideoFileClip(str(video_path))
        total_seconds += clip.duration  # Durata in secondi
        clip.close()  # Chiudi il video per liberare memoria
    
    total_minutes = int(total_seconds // 60)
    remaining_seconds = int(total_seconds % 60)
    
    risultato = f"La somma totale dei video è: {total_minutes} minuti e {remaining_seconds} secondi."
    
    return risultato

# pathVideo is a list of the Path of the videos
# courseName is the name of the course
# email is the email of the user
# Converter from mp4 to mp3
def useConverter(pathVideo, courseName, email, idRequest):
    
    start_time_main = time.time()

    print("Start Conversion", flush=True)

    duration = sumDurationVideo(pathVideo)
    
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
    timeConverter = end_time_main - start_time_main

    
    
    # Call Whisper for the transcription
    Whisper.main(pathList, courseName, email, timeConverter, duration, idRequest)