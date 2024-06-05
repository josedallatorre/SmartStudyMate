#Transform the mp3 into a text
import whisper
#import ChatGPT
from fpdf import FPDF
from pathlib import Path

pathPdf = Path("Pdf") 

def useWhisper(path, namePdf):
    #model = tiny, base, small, medium, large
    model = whisper.load_model("small",device="cuda")
    result = model.transcribe(path)
    transcribed_text = result["text"]
    print(transcribed_text)

    #save the transcribe in a file pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, transcribed_text)

    pdf.output(pathPdf / namePdf)

    
    #ChatGPT. useChatGpt(result["text"])



#useWhisper("Mp3/Test1.mp3", "Pdf1.pdf")



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