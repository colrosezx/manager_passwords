from cryptography.fernet import Fernet
from decouple import config

class PasswordManager:
    def __init__(self):
        self.key = config("KEY_ENCRYPTION")
        self.cipher_suite = Fernet(self.key)

    def encrypt_password(self, password):
        return self.cipher_suite.encrypt(password.encode())

    def decrypt_password(self, encrypted_password):
        try:
            if isinstance(encrypted_password, str):
                encrypted_password = encrypted_password.encode()
            decrypted = self.cipher_suite.decrypt(encrypted_password).decode('utf-8')
            return decrypted
        except Exception:
            raise Exception
        
password_manager = PasswordManager()