import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

from logging_setup import setup_logging
from main import scrapping

logger = setup_logging()

load_dotenv()

# Email credentials from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECEIVER_EMAILS = os.getenv('RECEIVER_EMAILS')  # Comma-separated emails
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
    message['To'] = ", ".join(RECEIVER_EMAILS)
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
            print(f"Warning: The file '{file_path}' does not exist and will not be attached.")
            logger.info(f"Warning: The file '{file_path}' does not exist and will not be attached.")
    
    return message

def send_email(message):
    """
    Sends an email using the configured SMTP server.
    
    :param message: MIMEMultipart email object
    """
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(message['From'], RECEIVER_EMAILS, message.as_string())
        print("Email sent successfully.")
        logger.info("Email sent successfully.")

    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    """
    Main function to handle the process of sending an email with attachments.
    """
    # Define the CSV files to attach
    csv_files = scrapping()  # Replace with actual file paths
    
    # Create the email
    subject = "CSV Files Attachment"
    body = "Please find the attached CSV files."
    message = create_email(subject, body, csv_files)
    
    # Send the email
    send_email(message)

if __name__ == "__main__":
    main()