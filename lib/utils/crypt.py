import base64
from os import getenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from dotenv import load_dotenv


class Crypt:
    def __init__(self):
        load_dotenv()
        secret = getenv("RPA_SECRET") or "secret"  # secret from .env
        secret = secret.encode()
        salt = b"salt_"
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        self.key = base64.urlsafe_b64encode(kdf.derive(secret))

    def encrypt(self, msg: str) -> str:
        """ Encrypts the message and returns the resulting string representation """
        f = Fernet(self.key)
        return f.encrypt(msg.encode()).decode()

    def decrypt(self, e_msg: str) -> str:
        """ Decrypts the encrypted messages and returns the value """
        f = Fernet(self.key)
        return f.decrypt(e_msg.encode()).decode()
