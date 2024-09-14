import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configurazione della mail di SmartStudyMate
from_email = "smartstudymateworkforyou@gmail.com"
from_password = "obzt yurm bygq exmh"
    
# Impostazioni del server SMTP di Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # Usa 465 per SSL o 587 per TLS

def send_email(to_email, file_path):
    
    subject = "Smart Study Mate: La tua dispensa è pronta!"
    
    # Creazione del messaggio
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    
    body = """Buone notizie!

La tua dispensa è pronta e puoi trovarla nel file in allegato.

Buono studio!



SmartStudyMate"""
    msg.attach(MIMEText(body, 'plain'))

    # Aggiunta allegato pdf 
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")

        msg.attach(part)

    # Connessione al server SMTP di Gmail
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(from_email, from_password)  # Esegui il login
        server.sendmail(from_email, to_email, msg.as_string())  # Invia la mail
        server.quit()
        print(f"Email inviata con successo a {to_email}")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {str(e)}")
