#Transform the mp3 into a text
#import ChatGPT
from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch
import os

pathPdf = Path("Pdf") 

def useWhisper(path, namePdf):

    if not os.path.exists("Pdf"):
      os.makedirs("Pdf")

    if namePdf.exists():
       return "File .pdf already exists"

    #model = tiny, base, small, medium, large
    model = pipeline(
        task="automatic-speech-recognition",        
        model="openai/whisper-large",
        device="cuda:0",
        torch_dtype=torch.float16,
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

