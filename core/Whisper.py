#Transform the mp3 into a text
import whisper
#import ChatGPT
from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch

pathPdf = Path("Pdf") 

def useWhisper(path, namePdf):
    #model = tiny, base, small, medium, large
    model = pipeline(
        task="automatic-speech-recognition",        
        model="GIanlucaRub/whisper-small-it-3",
        device="cuda:0",
        torch_dtype=torch.float16,
        chunk_length_s=30, # if not precised then only generate as much as max_new_tokens
        generate_kwargs={"num_beams": 5} # same setting as openai-whisper default
    )
    result = model(path)
    transcribed_text = result["text"]
    print(transcribed_text)

    #save the transcribe in a file pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, transcribed_text)

    pdf.output(pathPdf / namePdf)

    
    #ChatGPT. useChatGpt(result["text"])





#useWhisper("Mp3/Test1.mp3", "Pdf2.pdf")

#from openai import OpenAI
#client = OpenAI(
#    api_key = 'key'    
#)

#audio_file= open("Mp3/RiunioneDroniLezione1.mp3", "rb")
#transcription = client.audio.transcriptions.create(
#  model="whisper-1", 
#  file=audio_file
#)
#print(transcription.text)