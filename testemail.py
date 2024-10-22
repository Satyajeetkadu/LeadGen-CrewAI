import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to send an email via Gmail SMTP
def send_test_email(from_email, to_email, subject, body, smtp_server, smtp_port, login, password):
    # Create a MIME message object
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(login, password)  # Log in to your Gmail account
        text = msg.as_string()  # Convert message to a string
        server.sendmail(from_email, to_email, text)  # Send the email
        server.quit()  # Terminate the connection
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# Replace these variables with your email details
from_email = "satyajeetkadu74@gmail.com"  # Your Gmail email address
to_email = "SATYAJEET.KADU@nmims.in"  # The recipient's email address
subject = "Test Email from Python"
body = "This is a test email sent via Gmail SMTP using Python."
smtp_server = "smtp.gmail.com"
smtp_port = 587
login = "satyajeetkadu74@gmail.com"  # Your Gmail login email
password = ""  # Your Gmail password (or App Password if 2FA is enabled)

# Call the function to send a test email
send_test_email(from_email, to_email, subject, body, smtp_server, smtp_port, login, password)
