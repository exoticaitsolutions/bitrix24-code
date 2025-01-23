import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

from logging_setup import setup_logging

logger = setup_logging()

load_dotenv()

# Email credentials from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECEIVER_EMAILS = os.getenv('RECEIVER_EMAILS')  # Comma-separated 
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_HOST = os.getenv('SMTP_HOST')

def create_email(subject, body, files):
    """
    Creates an email with the specified subject, body, and attachments.
    
    :param subject: Email subject
    :param body: Email body content
    :param files: List of file paths to attach
    :return: MIMEMultipart email object
    """
    message = MIMEMultipart()
    message['From'] = EMAIL
    # Split the RECEIVER_EMAILS string by commas to ensure it's a list of email addresses
    receiver_list = RECEIVER_EMAILS.split(',')
    message['To'] = ", ".join(receiver_list)  # Use the list to join and form the 'To' field
    message['Subject'] = subject
    
    # Attach the email body
    message.attach(MIMEText(body, 'plain'))
    
    # Attach files
    for file_path in files:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                message.attach(part)
        else:
            logger.info(f"Warning: The file '{file_path}' does not exist and will not be attached.")
    
    return message


def send_email(message):
    """
    Sends an email using the configured SMTP server.
    
    :param message: MIMEMultipart email object
    """
    try:
        # Split the RECEIVER_EMAILS string by commas and pass it as a list
        recipients = RECEIVER_EMAILS.split(',')
        
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(message['From'], recipients, message.as_string())
        
        logger.info("Email sent successfully.")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")