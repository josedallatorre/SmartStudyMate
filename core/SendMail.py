import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuration of the email of SmartStudyMate
from_email = "smartstudymateworkforyou@gmail.com"
from_password = "obzt yurm bygq exmh"
    
# Setting of the Gmail server
smtp_server = "smtp.gmail.com"
smtp_port = 587  # 465 for SSL or 587 for TLS

# file_path is the path of the final file
# to_email is the email of the user
# Send the email with the final file as an attachment
def send_email(to_email, file_path):
    
    subject = "Smart Study Mate: La tua dispensa è pronta!"
    
    # Creation of the message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    
    body = """Buone notizie!

La tua dispensa è pronta e puoi trovarla nel file in allegato.

Buono studio!



SmartStudyMate"""
    msg.attach(MIMEText(body, 'plain'))

    # Add attachment
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")

        msg.attach(part)

    # Connection to the Gmail server
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() 
        server.login(from_email, from_password)  # login
        server.sendmail(from_email, to_email, msg.as_string())  # Send email
        server.quit()
        print(f"Email inviata con successo a {to_email}", flush=True)
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {str(e)}", flush=True)
