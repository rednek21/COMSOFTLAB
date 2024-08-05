import email
import base64
from imaplib import IMAP4_SSL


class IMAPClient:
    def __init__(self, server: str, port: int, email_addr: str, password: str):
        self.server = server
        self.port = port
        self.email_addr = email_addr
        self.password = password
        self.mail = IMAP4_SSL(self.server, self.port)

    def login(self):
        self.mail.login(self.email_addr, self.password)

    def select(self, box: str):
        self.mail.select(box)

    def search_emails(self, since_date=None):
        if since_date:
            search_criteria = f'(SINCE {since_date.strftime("%d-%b-%Y")})'
        else:
            search_criteria = 'ALL'
        typ, data = self.mail.search(None, search_criteria)
        return data[0].split()

    def fetch_email(self, email_id: str):
        typ, msg_data = self.mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        return msg

    @staticmethod
    def decode_mime_string(mime_str: str):
        parts = mime_str.split('?')
        charset = parts[1]
        encoding = parts[2]
        encoded_text = parts[3]

        if encoding.upper() == 'B':
            decoded_bytes = base64.b64decode(encoded_text)
        else:
            raise ValueError

        decoded_str = decoded_bytes.decode(charset)
        return decoded_str
