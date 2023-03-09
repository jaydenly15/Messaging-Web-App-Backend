import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sender_info():
    sender_email = "groupcamel123@gmail.com"
    sender_password = "Group_C@m3l"
    return sender_email, sender_password

def email_secret_code(email: str, secret_code: str) -> None:
    port = 465  # For SSL

    msg = MIMEMultipart()
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = 'UNSW Streams'
    msg['To'] = email

    text = f"Password Reset Code: {secret_code}"
    
    msg.attach(MIMEText(text, "plain"))

    context = ssl.create_default_context()
    print("Starting to send")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        sender_email, sender_password = sender_info()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
    print("Sent email")

