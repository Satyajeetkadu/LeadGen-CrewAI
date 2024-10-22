import re
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai import OpenAI  # Assuming you have the OpenAI package installed
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key and SMTP credentials from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
from_email = os.getenv("GMAIL_EMAIL")
password = os.getenv("GMAIL_APP_PASSWORD")

# Initialize OpenAI client with the API key from the .env file
client = OpenAI(api_key=openai_api_key)

# SMTP function to send an email
def send_email(from_email, to_email, subject, body, smtp_server, smtp_port, login, password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body to the message
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(login, password)  # Login to your Gmail account
        text = msg.as_string()  # Convert the message to string
        server.sendmail(from_email, to_email, text)  # Send the email
        server.quit()  # Close the connection
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

# Function to interactively get user input and build the search query
def get_user_input():
    industry_input = input("Which industries are you looking for leads in (comma-separated)? ")
    position_input = input("Which positions are you targeting (comma-separated)? ")
    country_input = input("Which country are you targeting? ")
    city_input = input("Which city are you targeting? ")
    user_name = input("What is your name? ")
    user_role = input("What is your current role or profession? ")
    purpose = input("Why are you reaching out (e.g., networking, potential collaboration)? ")
    
    industries = [industry.strip() for industry in industry_input.split(',')]
    positions = [position.strip() for position in position_input.split(',')]
    position_query = ' OR '.join(positions)
    industry_query = ' OR '.join(industries)
    email_query = '@gmail.com OR @yahoo.com OR @hotmail.com OR @outlook.com OR @ OR "email" OR "contact"'
    search_query = f'site:linkedin.com/in/ ({position_query}) -(saas or fintech) ({industry_query}) {email_query}, {city_input}, {country_input}'
    return search_query, city_input, country_input, user_name, user_role, purpose

# Function to generate email content using GPT-4
def generate_email(user_name, user_role, recipient_name, position, company, purpose):
    # Construct the prompt for GPT-4
    prompt = f"""
    Write a professional, personalized email to {recipient_name}, who works as {position} at {company}. 
    The purpose of the email is {purpose}. 
    The sender's name is {user_name}, and they are a {user_role}. 
    Make the email professional, engaging, and friendly.
    """
    
    # Use OpenAI GPT-4 to generate the email
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes professional emails."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the email content from the response
    email_body = completion.choices[0].message.content
    return email_body

# Initialize Serper tool with correct location
search_query, city_input, country_input, user_name, user_role, purpose = get_user_input()
tool = SerperDevTool(
    country="in",  
    locale="en",  
    location=f"{city_input}, {country_input}",  
    n_results=10,
)

# Execute the search
result = tool.run(search_query=search_query)

# Extract relevant details
profile_links = re.findall(r'https://[a-z]+\.linkedin\.com/in/[a-zA-Z0-9\-]+', result)
email_addresses = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', result)
titles = re.findall(r'Title: ([^\n]+)', result)
snippets = re.findall(r'Snippet: ([^\n]+)', result)

company_names = []
for title in titles:
    if " - " in title:
        company_names.append(title.split(" - ")[-1].strip())
    else:
        company_names.append("No Company")

# SMTP server details for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Generate emails using GPT-4 and send them using SMTP
print("\nGenerated and Sent Emails using GPT-4:")
for i in range(len(titles)):
    title = titles[i] if i < len(titles) else "No Title"
    link = profile_links[i] if i < len(profile_links) else "No Link"
    email = email_addresses[i] if i < len(email_addresses) else "No Email"
    company = company_names[i] if i < len(company_names) else "No Company"
    snippet = snippets[i] if i < len(snippets) else "No Snippet"
    recipient_name = title.split(" ")[0]
    
    # Generate email using GPT-4
    email_body = generate_email(user_name, user_role, recipient_name, title, company, purpose)
    
    print(f"Title: {title}")
    print(f"Link: {link}")
    print(f"Email: {email}")
    print(f"Company: {company}")
    print(f"Snippet: {snippet}")
    print("---")
    print(f"Generated Email:\n{email_body}")
    print("---")
    
    # Send the email
    if email != "No Email":
        send_email(
            from_email=from_email,
            to_email=email,  # Send to the extracted email address
            subject="Opportunity to Connect",
            body=email_body,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            login=from_email,  # Your Gmail email login
            password=password  # Your Gmail App Password
        )
    else:
        print(f"No valid email found for {recipient_name}. Skipping sending.")
