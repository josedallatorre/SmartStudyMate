from fpdf import FPDF
from pathlib import Path
from transformers import pipeline
import torch
import os
import PyPDF2
import time
import MultiAgents
import ffmpeg

# The model that is use to transcribe 
modelName = "openai/whisper-large"


# paths is the list of the .mp3 file to transcribe
# Function that uses whisper
def useWhisper(paths):
    listPdf = []
    model = pipeline(
        task="automatic-speech-recognition",
        model=modelName,
        device="cuda:0",
        torch_dtype=torch.float16,  # float32
    )

    for path in paths:
        start_time = time.time()

        # Create directory if doesn't exist
        if not os.path.exists("Pdf"):
            os.makedirs("Pdf")

        pathPdf = Path("Pdf") / str(path).split('/')[-1].replace(".mp3", ".pdf")
        listPdf.append((path, pathPdf))

        if not pathPdf.exists():
            try:
                # call Whisper
                result = model(str(path))
                transcribed_text = result["text"]
                print(f"Transcription for {path} completed in {time.time() - start_time} seconds.")
                print(transcribed_text)

                tt = transcribed_text.encode('latin-1', 'replace').decode('latin-1')

                # Save transcription
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, tt)
                pdf.output(str(pathPdf))

            except Exception as e:
                print(f"Error processing {path}: {e}", flush=True)
                continue

            finally:
                # Release resources
                print(f"Cleanup for {path} completed.", flush=True)

    return listPdf

# paths is a list of the Path of the .mp3
# courseName is the name of the course
# email is the email of the user
def main(paths, courseName, email, timeConverter, duration, idRequest):
    
    start_time_main = time.time()

    print("Start transcription", flush=True)
    
    # Execute Whisper for all the files sequentially
    listPdf = useWhisper(paths)

    # Order the Pdf as the order of Mp3
    listPdf.sort(key=lambda x: paths.index(x[0]))

    # Extract only the pdf path
    pdf_paths = [pdf_path for _, pdf_path in listPdf]

    print("Finish transcription", flush=True)

    end_time_main = time.time()
    total_time = end_time_main - start_time_main

    timeConverterWhisper = timeConverter + total_time

    # Call model for the creation
    MultiAgents.firstStep(pdf_paths, courseName, email, timeConverterWhisper, duration, idRequest)