import pytest
from app.core.encryption import encrypt, decrypt

@pytest.mark.parametrize("plaintext", [
    "bank_account_number_123456789", # Test with a typical sensitive string
    "1234.56", # Test with a numeric string
    "secret-note-with-emoji-😉",
    "", # Test with an empty string
    "a" * 1000 # Test with a long string
])
def test_encryption_decrypt_roundtrip(plaintext):
    """
    Test that encrypting and then decrypting a plaintext string returns the original plaintext, ensuring that the encryption and decryption functions are consistent and correctly implemented.
     The test uses a variety of input strings, including typical sensitive data, numeric strings, strings with emojis, empty strings, and long strings to ensure that the functions work correctly across different types of input.
     The assertions check that the encrypted value is a string, is significantly longer than the plaintext (indicating that encryption is occurring), is not the same as the plaintext, and that decrypting the encrypted value returns the original plaintext.
    
    :param plaintext: The plaintext string to be encrypted and decrypted in the test. This can be any string, including typical sensitive data, numeric strings, strings with emojis, empty strings, or long strings.
    :type plaintext: LiteralString | Literal['bank_account_number_123456789', '1234.56', 'secret-note-with-emoji-😉', '']
    """
    encrypted = encrypt(plaintext)
    decrypted = decrypt(encrypted)

    assert isinstance(encrypted, str), "Encrypted value should be a string"
    assert len(encrypted) > 20, "Encrypted value should be significantly longer than the plaintext"
    assert encrypted != plaintext, "Encrypted value should not be the same as the plaintext"
    assert decrypted == plaintext, "Decrypted value should match the original plaintext"

def test_decrypt_invalid_token():
    """
    Test that decrypting an invalid token returns None, ensuring that the decryption function correctly handles tampered or malformed ciphertext without throwing an exception.
     This is important for security, as it prevents potential crashes or information leaks when invalid data is encountered.
     The test uses a string that is not a valid Fernet token, which should trigger the InvalidToken exception and result in the decrypt function returning None.
     Valid Fernet tokens are 128 characters long and start with 'gAAAAAB', so the provided string is intentionally malformed to test this behavior.
    """
    invalid_cipher = "gAAAAABinvalidtamperedciphertext==" # This is not a valid Fernet token, valid tokens are 128 characters long and start with 'gAAAAAB'
    decrypted = decrypt(invalid_cipher)
    
    assert decrypted is None, "Decryption of an invalid token should return None"

def test_decrypt_empty_string():
    """
    Test that decrypting an empty string returns None, and that encrypting an empty string returns a valid encrypted string.
     This ensures that the encryption and decryption functions handle empty inputs gracefully without errors.
    """
    encrypted = encrypt("")
    decrypted = decrypt(encrypted)

    assert isinstance(encrypted, str), "Encrypted value should be a string even for empty input"
    assert len(encrypted) > 20, "Encrypted value should still be significantly longer than the plaintext (which is empty)"
    assert decrypted == "", "Decrypted value of an encrypted empty string should be an empty string"

def test_encrypt_empty_input():
    """
    Test that encrypting None returns an empty string and decrypting it returns None.
    This ensures that the encryption and decryption functions handle empty or None inputs gracefully.
    """
    encrypted = encrypt(None)
    decrypted = decrypt(encrypted)

    assert encrypted == "", "Encrypting None should return an empty string"
    assert decrypted is None, "Decrypting an empty string should return None"