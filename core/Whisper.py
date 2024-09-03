from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch
import os
import PyPDF2
from concurrent.futures import ThreadPoolExecutor
import time

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

      # Creare directory per i PDF se non esiste
      if not os.path.exists("Pdf"):
          os.makedirs("Pdf")

      pathPdf = Path("Pdf") / (path.stem + ".pdf")
      listPdf.append((path, pathPdf))

      if not pathPdf.exists():
          # Chiamata al modello Whisper per la trascrizione
          result = model(str(path))
          transcribed_text = result["text"]
          print(f"Transcription for {path} completed in {time.time() - start_time} seconds.")
          print(transcribed_text)

          tt = transcribed_text.encode('latin-1', 'replace').decode('latin-1')

          # Salvare la trascrizione in un file PDF
          pdf = FPDF()
          pdf.add_page()
          pdf.set_font("Arial", size=12)
          pdf.multi_cell(0, 10, tt)
          pdf.output(str(pathPdf))

  return listPdf

# Funzione principale per gestire il parallelismo
def main(paths):
    # Dividere la lista in due parti
    half = len(paths) // 2
    paths1 = paths[:half]
    paths2 = paths[half:]

    # Eseguire Whisper in parallelo su entrambe le liste
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(useWhisper, paths1), executor.submit(useWhisper, paths2)]

    listPdf = []
    for future in futures:
        listPdf.extend(future.result())

    # Ordinare i PDF in base all'ordine originale dei file MP3
    listPdf.sort(key=lambda x: paths.index(x[0]))

    # Estrarre solo i percorsi dei PDF
    pdf_paths = [pdf_path for _, pdf_path in listPdf]
