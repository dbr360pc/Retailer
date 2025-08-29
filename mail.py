import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def sendEmail(retailer_name,response,receiver_email='it@nemausa.com'):
    sender_email = "dbrnotifications@gmail.com"
    app_password = "onev ggie znql gias"
    receiver_email = receiver_email

    if response.get('status') == False:
        subject = f"Error in {retailer_name} Scraping"
        body = f"An error occurred during the {retailer_name} scraping process:\n\n{response.get('message', 'No details provided')}"
    else:
        subject = f"{retailer_name} Scraping Completed"
        body = f"The {retailer_name} scraping process has been completed successfully."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        print("Notification sent successfully!")
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")