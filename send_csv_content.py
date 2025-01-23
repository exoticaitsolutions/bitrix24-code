import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from logging_setup import setup_logging


logger = setup_logging()


# Email credentials from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECEIVER_EMAILS = os.getenv('RECEIVER_EMAILS')  # Comma-separated 
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_HOST = os.getenv('SMTP_HOST')

# CSV files to read
csv_files = ['My Chart - Bids per Bidder.csv', 'My Chart - Job Category wise for Deals each stage.csv']

# Combine data from all CSV files into a single string
csv_content = ""
for file in csv_files:
    try:
        data = pd.read_csv(file)
        csv_content += f"\nData from {file}:\n{data.to_string(index=False)}\n"
    except FileNotFoundError:
        csv_content += f"\nFile {file} not found.\n"
    except Exception as e:
        csv_content += f"\nAn error occurred while reading {file}: {e}\n"

# Create the email
message = MIMEMultipart()
message['From'] = EMAIL
message['To'] = ", ".join(RECEIVER_EMAILS)
message['Subject'] = "CSV Data Report"

# Attach the CSV data as plain text
message.attach(MIMEText(csv_content, 'plain'))

# Send the email
try:
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, RECEIVER_EMAILS, message.as_string())
        logger.info("Email sent successfully.")
        
except Exception as e:
    logger.error(f"Failed to send email: {e}")
