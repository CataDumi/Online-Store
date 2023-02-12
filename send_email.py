import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(name, email, phone, message, invoice):
    host = "smtp.gmail.com"
    port = 465
    sender = 'catastudent.32@gmail.com'
    password = 'dhenhscrkhymvozk'
    receiver = 'catastudent.32@gmail.com'

    msg = MIMEMultipart()
    text = f'{message}'
    msg['Subject'] = f"Online store -  user {name} sent you an email - {phone}"
    msg['From'] = email
    msg['To'] = 'Admin'

    # Insert the text to the msg going by e-mail
    msg.attach(MIMEText(text, "plain"))

    if invoice == True:
        default_msg = f'''Dear valued customer,\n
We wanted to take a moment to express our heartfelt gratitude for choosing to shop with us at our website store. 
Your purchase helps support our mission, and we truly appreciate your business.
Our goal is to provide you with an exceptional shopping experience, and we are thrilled to have met that goal.\n
We are committed to providing you with high-quality products and exceptional customer service, and it means the world to us that you have placed your trust in us.
We hope that you are completely satisfied with your purchase and that you will continue to shop with us for all of your future needs. \n
If there is anything we can do to improve your experience, please do not hesitate to reach out to us.
Thank you once again for your support, and we look forward to serving you again soon.
        '''
        msg.attach(MIMEText(default_msg, "plain"))

        # Attach the pdf to the msg going by e-mail
        with open('static/files/invoice.pdf', "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
        msg.attach(attach)

    with smtplib.SMTP("smtp.gmail.com", ) as server:
        server.starttls() and server.login(user=sender, password=password)
        server.sendmail(from_addr=sender,
                        to_addrs=receiver,
                        msg=msg.as_string())
