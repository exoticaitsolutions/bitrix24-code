from send_email_setup import create_email, send_email
from utils import scrapping

def main():
    """
    Main function to handle the process of sending an email with attachments.
    """
    # Define the CSV files to attach
    csv_files = scrapping()  # Replace with actual file paths
    
    # Create the email
    subject = "CSV Files Attachment of Bitrix24"
    body = "Please find the attached Bitrix24 CSV files."
    message = create_email(subject, body, csv_files)
    
    # Send the email
    send_email(message)

if __name__ == "__main__":
    main()