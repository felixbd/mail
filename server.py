#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
E-Mail-Server - (c) 2023 Felix Drees - Use at your own risk, no warranty, no support, no liability!
"""

import socket
from socket import AF_INET as IPv4, SOCK_STREAM as TCP
import threading
from datetime import datetime
import logging

from smtp_status_codes import SUCCESSFUL, UNDERSTOOD, TEMP_ERROR, FATAL_ERROR, STATUS_CODES

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S',
                    filename='mail_server.log')
logging.getLogger().addHandler(logging.StreamHandler())

HOST = 'localhost'
PORT = 4202
MAX_CONNECTIONS = 5

__coding__ = 'utf-8'

MODERN_SMTP_COMMANDS = [
    # ---- implemented ----
    'HELO',  # initial greeting
    'EHLO',  # extended initial greeting
    'MAIL',  # transfer mail of sender
    'RCPT',  # transfer mail of recipient
    'DATA',  # start mail content transfer
    'RSET',  # reset data transfer
    'NOOP',  # no operation
    'QUIT',  # end session
    # ---- not jet implemented ----
    'CHNK',
    'X-EXPS',
    'SEND',
    'DSN',
    'BURL',
    'X-EXCH50',
    'ATRN',
    'BINARYMIME',
    'XSTA',
    '8BITMIME',
    'HELP',
    'AUTH',
    'ETRN',
    'PIPELINING',
    'TURN',
    'ENHANCEDSTATUSCODES',
    'VRFY',
    'STARTTLS',
    'X-LINK2STATE',
    'EXPN',
    'XADR',
    'CHUNKING',
    'ONEX',
    'SOML',
    'VERB',
    'SAML',
    'BDAT',
    'SIZE'
]


def handle_client(client_socket) -> None:
    client_socket.send(b'220 SMTP Server Ready\r\n')
    start_time = datetime.now()
    client_name, send_client_name = "{0}:{1}".format(*client_socket.getpeername()), '-'

    esmtp_mode = False
    pipline_mode = False

    while True:
        data = client_socket.recv(1024).decode(__coding__).strip()

        if not data:
            break

        for command in [data] if not pipline_mode else data.split('\r\n'):

            # in smtp all commands used to be 4 characters long but in esmtp they can be longer
            #  (lambda s: [s[:4].upper(), s[5:]])(command)

            match (lambda x: [x.split()[0].upper(), ''.join(x.split()[1:])])(command):
                case ['EHLO', send_client_name]:
                    # “Extended Hello” – the client identifies itself to the server and
                    #  indicates that it wants to use the Extended SMTP (ESMTP) protocol.
                    logging.info(f"incoming EHLO from {client_name}, send client name: {send_client_name}")
                    esmtp_mode = True

                    response = f'250-Hello {send_client_name}, I am glad to meet you\r\n'.encode(__coding__)
                    response += b'250-PIPELINING\r\n'
                    response += b'250-AUTH LOGIN PLAIN\r\n'
                    response += b'250 Ok\r\n'

                    logging.info(f"outgoing EHLO to {client_name}, say hello to {send_client_name}")
                    client_socket.send(response)

                case ['HELO', send_client_name]:
                    # “Hello.”– the client logs on with its computer name and starts the session with the HELO command.
                    logging.info(f"incoming HELO from {client_name}, send client name: {send_client_name}")

                    response = f'250 Hello {send_client_name}, I am glad to meet you\r\n'.encode(__coding__)

                    logging.info(f"outgoing HELO to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['MAIL', from_email_address]:
                    # The client names the sender of the e-mail with the MAIL command.
                    logging.info(f"incoming MAIL from {client_name}, from email address: {from_email_address}")

                    response = b'250 Ok\r\n'

                    logging.info(f"outgoing MAIL to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['RCPT', recipient_email_address]:
                    # “Recipient” – the client names the recipient of the e-mail with the RCPT command.
                    logging.info(
                        f"incoming RCPT from {client_name}, recipient email address: {recipient_email_address}")

                    response = b'250 Ok\r\n'

                    logging.info(f"outgoing RCPT to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['DATA', tail]:
                    # The client initiates the transmission of the e-mail content with the DATA command.
                    logging.info(f"incoming DATA from {client_name}, tail: {tail}")

                    response = b'354 Start mail input; end with <CRLF>.<CRLF>\r\n'

                    logging.info(f"outgoing DATA to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                    logging.info(f"incoming DATA from {client_name}, accumulating data")
                    email_data = b''
                    while True:
                        data = client_socket.recv(1024)
                        email_data += data
                        if data.endswith(b'\r\n.\r\n'):
                            break
                    logging.info(f"incoming DATA from {client_name}, done accumulating data")

                    email_data += f"\nST:{str(start_time)} -> ET:{str(datetime.now())}\n".encode(__coding__)
                    email_data += f"{client_name} {send_client_name}\n".encode(__coding__)
                    email_data += b"=" * 80 + b"\n"

                    logging.info(f"incoming DATA from {client_name}, writing to file")
                    with open("received_mails.txt", "a") as file:
                        file.write(email_data.decode(__coding__))

                    logging.info(f"outgoing DATA to {client_name}, response: 250 Ok")
                    client_socket.send(b'250 Ok\r\n')

                case ['RSET', tail]:
                    # The client terminates the initiated transmission,
                    #  but maintains the connection between client and server
                    logging.info(f"incoming RSET from {client_name}, tail: {tail}")

                    response = b'250 Ok\r\n'

                    logging.info(f"outgoing RSET to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['NOOP', tail]:
                    # “No operation” – the client or server sends this command to test the connection to the other side.
                    logging.info(f"incoming NOOP from {client_name}, tail: {tail}")

                    response = b'250 Ok\r\n'

                    logging.info(f"outgoing NOOP to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['VRFY' | 'EXPN', tail]:
                    # “Verify”/“Expand”– the client checks whether a mailbox is available for message transmission.
                    logging.info(f"incoming VRFY/EXPN from {client_name}, tail: {tail}")

                    response = b'252 Ok\r\n'

                    logging.info(f"outgoing VRFY/EXPN to {client_name}, response: {response.decode(__coding__)}")
                    client_socket.send(response)

                case ['QUIT', tail]:
                    logging.info(f"incoming QUIT from {client_name}, tail: {tail}")
                    logging.info(f"outgoing QUIT to {client_name}, response: 221 Bye")
                    client_socket.send(b'221 Bye\r\n')
                    break

                case [unknown_command, tail]:
                    logging.info(
                        f"incoming unknown command from {client_name}, unknown command: {unknown_command}, tail: {tail}")
                    logging.info(f"outgoing unknown command to {client_name}, response: 500 Command not recognized")
                    client_socket.send(b'500 Command not recognized\r\n')

                case _ as other:
                    logging.info(f"incoming unknown command from {client_name}, other: {other}")
                    logging.info(f"outgoing unknown command to {client_name}, response: 500 Command not recognized")
                    client_socket.send(b'500 Command not recognized\r\n')

    logging.info(f"Closing connection to {client_name}")
    client_socket.close()


def start_server():
    # Start the server and wait for incoming connections.
    try:
        with socket.socket(IPv4, TCP) as mail_server:
            mail_server.bind((HOST, PORT))
            mail_server.listen(MAX_CONNECTIONS)
            print(f"Mail-Server running on {HOST}:{PORT}")

            while True:
                # Wait for incoming connections and handle them each in a new thread.
                client_socket, client_address = mail_server.accept()
                print(f"New connection from {client_address[0]}:{client_address[1]}")
                client_handler = threading.Thread(target=handle_client, args=(client_socket,))
                client_handler.start()
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    start_server()
