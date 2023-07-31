import smtplib

host, port = 'localhost', 4202


def send_email_client():
    sender = 'your_email@example.com'
    receiver = 'recipient@example.com'
    subject = 'Test Subject'
    body = 'This is a test email.'

    message = f"From: {sender}\r\n" \
              f"To: {receiver}\r\n" \
              f"Subject: {subject}\r\n\r\n{body}"

    with smtplib.SMTP(host, port) as server:
        server.sendmail(sender, receiver, message)


if __name__ == "__main__":
    send_email_client()
