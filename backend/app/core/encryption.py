import os
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError("FERNET_KEY environment variable is not set")

fernet = Fernet(FERNET_KEY.encode()) # Ensure the key 32-byte string is properly encoded

def encrypt(plaintext: Optional[str]) -> str:
    """
    Encrypts a plaintext string using Fernet symmetric encryption. If the input is None, returns an empty string.
    
    :param plaintext: The plaintext string to be encrypted. If the input is None, the function will return an empty string.
    :type plaintext: Optional[str]
    :return: The encrypted string as a regular string. If the input is None, returns an empty string.
    :rtype: str
    """
    if plaintext is None:
        return ""
    encrypted_bytes = fernet.encrypt(plaintext.encode())
    return encrypted_bytes.decode() # Return the encrypted string as a regular string

def decrypt(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decrypts a ciphertext string using Fernet symmetric encryption. If the ciphertext is invalid or None, returns None.
    
    :param ciphertext: The encrypted string to be decrypted. This should be a valid Fernet token. If the input is None or invalid, the function will return None.
    :type ciphertext: Optional[str]
    :return: The decrypted plaintext string if decryption is successful, or None if the input is invalid or decryption fails.
    :rtype: str | None
    """
    if not ciphertext:
        return None
    try:
        decrypted_bytes = fernet.decrypt(ciphertext.encode())
        return decrypted_bytes.decode() # Return the decrypted string as a regular string
    except InvalidToken:
        return None