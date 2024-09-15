from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch
import os
import PyPDF2
from concurrent.futures import ThreadPoolExecutor
import time
import MultiAgents
import ffmpeg

pathPdf = Path("Pdf")


def useWhisper(paths):
  listPdf = []
  model = pipeline(
    task="automatic-speech-recognition",
    model="openai/whisper-large",
    device="cuda:0",
    torch_dtype=torch.float16,  # float32
  )

  for path in paths:
      start_time = time.time()

      #Create directory if doesn't exist
      if not os.path.exists("Pdf"):
          os.makedirs("Pdf")

      pathPdf = Path("Pdf") / str(path).split('/')[-1].replace(".mp3", ".pdf")
      listPdf.append((path, pathPdf))

      if not pathPdf.exists():
          # Call to Whisper model
          result = model(str(path))
          transcribed_text = result["text"]
          print(f"Transcription for {path} completed in {time.time() - start_time} seconds.")
          print(transcribed_text)

          tt = transcribed_text.encode('latin-1', 'replace').decode('latin-1')

          # Save the transcription as a Pdf
          pdf = FPDF()
          pdf.add_page()
          pdf.set_font("Arial", size=12)
          pdf.multi_cell(0, 10, tt)
          pdf.output(str(pathPdf))

  return listPdf

# Function for parallelism
def main(paths, courseName, email):
    
    half = len(paths) // 2
    paths1 = paths[:half]
    paths2 = paths[half:]

    # Execute Whisper fot the two list
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(useWhisper, paths1), executor.submit(useWhisper, paths2)]

    listPdf = []
    for future in futures:
        listPdf.extend(future.result())

    # Order the Pdf as the order of Mp3
    listPdf.sort(key=lambda x: paths.index(x[0]))

    # Extract only the pdf path
    pdf_paths = [pdf_path for _, pdf_path in listPdf]

    #call model for the creation
    MultiAgents.firstStep(pdf_paths, courseName, email)
