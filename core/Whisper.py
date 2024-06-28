#Transform the mp3 into a text
#import ChatGPT
from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch
import os
import PyPDF2

pathPdf = Path("Pdf") 


#merge the pdfs
def merge_pdfs(pdf_paths, output_path):

    if not os.path.exists("Merged"):
       os.makedirs("Merged")
    pdf_writer = PyPDF2.PdfWriter ()

    for pdf_path in pdf_paths:
        pdf_reader = PyPDF2.PdfReader(str(pdf_path))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output_path, 'wb') as out_file:
        pdf_writer.write(out_file)


def useWhisper(pathMp3):

    listPdf = []

    for path in pathMp3:

      #Converter
      #Call whisper for the transcription
      if not os.path.exists("Pdf"):
        os.makedirs("Pdf")

      pathPdf = Path("Pdf") / (str(path).replace(".mp3", ".pdf").replace("Mp3/", ""))

      listPdf = listPdf + [pathPdf]
      model = pipeline(
        task="automatic-speech-recognition",        
        model="openai/whisper-large",
        device="cuda:0",
        torch_dtype=torch.float16,
      )

      if not pathPdf.exists():
      
        #model = tiny, base, small, medium, large

        result = model(str(path))
        transcribed_text = result["text"]
        print(transcribed_text)

        tt= transcribed_text.encode('latin-1', 'replace').decode('latin-1')

        #save the transcribe in a file pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, tt)

        pdf.output(pathPdf)

      merge_pdfs(listPdf, Path("Merged/merge.pdf"))
    
    