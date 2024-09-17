from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import transformers
import torch
import gc
import os
from fpdf import FPDF
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import aspose.pdf as ap 
import SendMail

torch.cuda.empty_cache()
gc.collect()

device="cuda:0"

# Model for the text generation
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-14B-Chat",
    torch_dtype=torch.float16,
    device_map=device,
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-14B-Chat")

# filePath is the path of the pdf
# Transform the pdf in a text
def readPdf(filePath):
    
    with open(filePath, 'rb') as file:        
        reader = PyPDF2.PdfReader(file)                 
        testo = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            testo += page.extract_text()               
        return testo

# text is the course name
# create the title for the final output
def createTitle(text):

    pdf = FPDF()
    pdf.add_page()
    

    pdf.set_font("Arial", size=25)
    
    text_width = pdf.get_string_width(text)
    page_width = pdf.w - 2 * pdf.l_margin
    
    x_position = (page_width - text_width) / 2 + pdf.l_margin
    
    pdf.set_y(80)  # 70 mm = 7 cm
    
    pdf.multi_cell(0, 10, text, align='C') 
    

    path = "Generate/Step1/" + text + ".pdf"
    pdf.output(str(path))
    

    
# pdfPaths is a list of the Path of the pdf
# courseName is the name of the course
# email is the email of the user
# Generate the summary for every pdf
def firstStep(pdfPaths, courseName, email):

    listResume = []
    name= ""

    for path in pdfPaths:
        
        pathResume = Path("Generate/Step1") / str(path).split('/')[-1]
        listResume.append(str(pathResume))
        
        if not pathResume.exists():
            testoPdf = readPdf(path);
            # read the pdf and put it in the message
            messages = [
                {"role": "user", "content": testoPdf },
            ]
            print(len(messages[0]["content"]))
            length_context=5000
            messages = [{"role":x["role"],"content":m} for x in messages for m in [ x["content"][i:i+length_context] for i in range(0, int(len(x["content"])), length_context) ]]
            #print(messages)

            totale= ""

            for m in messages:
                torch.cuda.empty_cache()
                gc.collect()
                m["content"]=f"""Ciao, sei un agente specializzato nell'organizzazione dei contenuti, di seguito troverai la trascrizione di una lezione universitaria. Il tuo compito è di fornire un singolo argomento o tema principale che riassuma l'intera trascrizione. Rispondi con una sola parola o una breve frase coincisa: \" {m["content"]} \" """
                text = tokenizer.apply_chat_template(
                    [m],
                    tokenize=False,
                    add_generation_prompt=True
                )

                torch.cuda.empty_cache()
                gc.collect()

                model_inputs = tokenizer([text], return_tensors="pt").to(device)

                generated_ids = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=2048
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                #print(response+"\n\n\n\n")

                totale= totale + response + " ---- "

            #print(totale)

            # create the dir
            if not os.path.exists("Generate/Step1"):
                os.makedirs("Generate/Step1")    


            tt= totale.encode('latin-1', 'replace').decode('latin-1')

            # save the resume in a file pdf
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, tt)
            pdf.output(str(pathResume))

    pathCouseName= "Generate/Step1/" + courseName + ".pdf"
    createTitle(courseName)
    secondStep(pdfPaths, listResume, pathCouseName, email)
        
# test is the text 
# Extract the element from a text
def estrai_elementi(test):
    # Divide the text with "----"
    elementi = test.split("----")
    listElementi = []
    
    # remove white space
    elementi = [e.strip() for e in elementi if e.strip()]
    
    for elemento in elementi:
        listElementi.append(elemento) 

    return listElementi


# pdfPaths is a list of the Path of the pdf
# argumentPath is the path with the argument of a pdf
# courseName is the name of the course
# email is the email of the user
# from an argument generate the answer
def secondStep(pdfPaths, argomentPath, pathCouseName, email):

    listResume = []
    listArgomenti = []
    name= ""

    for i in range(len(pdfPaths)):

        pathResume = Path("Generate/Step2") / str(pdfPaths[i]).split('/')[-1]
        listResume.append(pathResume)

        if not pathResume.exists():

            testoPdf = readPdf(pdfPaths[i])
            # read the pdf and put it in the message
            messages = [
                {"role": "user", "content": testoPdf },
            ]
            print(len(messages[0]["content"]))
            length_context=5000
            messages = [{"role":x["role"],"content":m} for x in messages for m in [ x["content"][i:i+length_context] for i in range(0, int(len(x["content"])), length_context) ]]
            #print(messages)

            totale= ""

            argomenti = readPdf(argomentPath[i])

            listArgomenti = estrai_elementi(argomenti)

            j=0
            for m in messages:
                torch.cuda.empty_cache()
                gc.collect()
                m["content"]=f"""Ciao, sei un agente specializzato nella spiegazione di argomenti specifici. Dato questo argomento: {listArgomenti[j]}, il tuo compito è quello di fornire una spiegazione dettagliata e approfondita, senza includere introduzioni, conclusioni, riferimenti a corsi, esami o altro contesto accademico. Devi concentrarti esclusivamente sui dettagli tecnici e specifici dell'argomento, mantenendo la spiegazione scorrevole e priva di qualsiasi riferimento a corsi o contesti didattici. Non menzionare esami, partecipanti, studenti o qualsiasi altra informazione estranea. Limita la tua risposta solo a spiegare l'argomento nel modo più chiaro e completo possibile. Ecco il testo: \" {m["content"]} \" """
                text = tokenizer.apply_chat_template(
                    [m],
                    tokenize=False,
                    add_generation_prompt=True
                )
                

                torch.cuda.empty_cache()
                gc.collect()

                model_inputs = tokenizer([text], return_tensors="pt").to(device)

                generated_ids = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=2048
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                #print(response+"\n\n\n\n")

                totale= totale + listArgomenti[j] + "\n\n\n" + response + "\n\n\n\n\n"

                j=j+1
                

            #print(totale)

            # create the dir
            if not os.path.exists("Generate/Step2"):
                os.makedirs("Generate/Step2")    


            tt= totale.encode('latin-1', 'replace').decode('latin-1')

            # save the resume in a file pdf
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, tt)
            pdf.output(str(pathResume))

    thirdStep(listResume, pathCouseName, email)



# pdfPaths is a list of the Path of the pdf
# courseName is the name of the course
# email is the email of the user
# from a pdf generate the question 
def thirdStep(pdfPaths, pathCouseName, email):

    listResume = []

    iterator = 1

    name= ""

    for path in pdfPaths:

        pathResume = Path("Generate/Step3") / str(path).split('/')[-1]
        listResume.append(pathResume)

        if not pathResume.exists():

            testoPdf = readPdf(path)
            #read the pdf and put it in the message
            messages = [
                {"role": "user", "content": testoPdf },
            ]
            print(len(messages[0]["content"]))
            length_context=5000
            messages = [{"role":x["role"],"content":m} for x in messages for m in [ x["content"][i:i+length_context] for i in range(0, int(len(x["content"])), length_context) ]]
            #print(messages)

            totale= ""

            for m in messages:
                
                torch.cuda.empty_cache()
                gc.collect()
                m["content"]=f"""Ciao, sei un agente specializzato nel creare domande legate ad un testo. Il tuo compito è andare a creare una singola domanda per il testo che ti metterò di seguito. Questa domanda deve essere generale, per fare in modo che lo studente possa rispondere in maniera completa. Ecco il testo: \" {m["content"]} \" """
                text = tokenizer.apply_chat_template(
                    [m],
                    tokenize=False,
                    add_generation_prompt=True
                )
                

                torch.cuda.empty_cache()
                gc.collect()

                model_inputs = tokenizer([text], return_tensors="pt").to(device)

                generated_ids = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=2048
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                #print(response+"\n\n\n\n")

                totale= totale + str(iterator) + ") "+ response + " ---- " + "\n"

                iterator=iterator+1
                

            #print(totale)

            #create the dir
            if not os.path.exists("Generate/Step3"):
                os.makedirs("Generate/Step3")    


            tt= totale.encode('latin-1', 'replace').decode('latin-1')

            #save the resume in a file pdf
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, tt)
            pdf.output(str(pathResume))

    fourthStep(pdfPaths, listResume, pathCouseName, email)
    

# pdfPaths is a list of the Path of the pdf
# domandePath is a list of the Path of the question
# courseName is the name of the course
# email is the email of the user
# from the question generate the answer 
def fourthStep(pdfPaths, domandePath, pathCouseName, email):

    listResume = []
    listDomande = []
    name= ""
    totale= "RISPOSTE" + "\n\n\n"
    iterator = 1

    for i in range(len(pdfPaths)):

        pathResume = Path("Generate/Step4") / str(pdfPaths[i]).split('/')[-1]
        listResume.append(pathResume)

        if not pathResume.exists():

            testoPdf = readPdf(pdfPaths[i])
            # read the pdf and put it in the message
            messages = [
                {"role": "user", "content": testoPdf },
            ]
            print(len(messages[0]["content"]))
            length_context=5000
            messages = [{"role":x["role"],"content":m} for x in messages for m in [ x["content"][i:i+length_context] for i in range(0, int(len(x["content"])), length_context) ]]
            #print(messages)


            argomenti = readPdf(domandePath[i])

            listDomande = estrai_elementi(argomenti)

            j=0
            for m in messages:
                torch.cuda.empty_cache()
                gc.collect()
                m["content"]=f"""Ciao, sei un agente specializzato nel rispondere alle domande. Data questa domanda: {listDomande[j]}, il tuo compito è quello di fornire una risposta dettagliata in base al testo che ti passo. Dammi solo la risposta diretta. Ecco il testo: \" {m["content"]} \" """
                text = tokenizer.apply_chat_template(
                    [m],
                    tokenize=False,
                    add_generation_prompt=True
                )
                

                torch.cuda.empty_cache()
                gc.collect()

                model_inputs = tokenizer([text], return_tensors="pt").to(device)

                generated_ids = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=2048
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                print(response+"\n\n\n\n")

                totale= totale + "Risposta " + str(iterator) + ") " + response + "\n\n"

                j=j+1
                iterator=iterator+1
                

            #print(totale)

            # create the dir
        if not os.path.exists("Generate/Step4"):
            os.makedirs("Generate/Step4")    


        pathResume = Path("Generate/Step4") / str(pdfPaths[i]).split('/')[-1]
        listResume.append(pathResume)
        tt= totale.encode('latin-1', 'replace').decode('latin-1')

        # save the resume in a file pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, tt)
        pdf.output(str(pathResume))


    fifthStep(pdfPaths, domandePath, pathResume, pathCouseName, email)

# create blank page
def create_blank_page():
    """Create blank page"""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.showPage()
    can.save()
    packet.seek(0)
    return PdfReader(packet)


# listPaths is a list of the Path of the pdf
# listDomande is a list of the Path of the pdf
# Risposte is a list of the Path of the pdf
# courseName is the name of the course
# email is the email of the user
# generate the final output
def fifthStep(listPaths, listDomande, Risposte, pathCouseName, email):

    outputPath = Path("Generate/Step5") / str(pathCouseName).split('/')[-1]

    if not outputPath.exists():
        writer = PdfWriter()
        reader_pdf = PdfReader(str(pathCouseName))

        # add the page to the final document
        for page in reader_pdf.pages:
            writer.add_page(page)

        for pdf_path, domande_path in zip(listPaths, listDomande):
            
            reader_pdf = PdfReader(str(pdf_path))
            for page in reader_pdf.pages:
                writer.add_page(page)
            
            # add question
            reader_domande = PdfReader(str(domande_path))
            for page in reader_domande.pages:
                writer.add_page(page)

            blank_page = create_blank_page()
            writer.add_page(blank_page.pages[0])

        blank_page = create_blank_page()
        writer.add_page(blank_page.pages[0])

        # add answer
        reader_risposte = PdfReader(str(Risposte))
        for page in reader_risposte.pages:
            writer.add_page(page)

        if not os.path.exists("Generate/Step5"):
            os.makedirs("Generate/Step5")   


        # save the final pdf
        with open(outputPath, "wb") as output_pdf:
            writer.write(output_pdf)

    SendMail.send_email(email, outputPath)
