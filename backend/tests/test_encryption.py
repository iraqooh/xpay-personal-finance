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
    encrypted = encrypt(plaintext)
    decrypted = decrypt(encrypted)

    assert isinstance(encrypted, str), "Encrypted value should be a string"
    assert len(encrypted) > 20, "Encrypted value should be significantly longer than the plaintext"
    assert encrypted != plaintext, "Encrypted value should not be the same as the plaintext"
    assert decrypted == plaintext, "Decrypted value should match the original plaintext"

def test_decrypt_invalid_token():
    invalid_cipher = "gAAAAABinvalidtamperedciphertext==" # This is not a valid Fernet token, valid tokens are 128 characters long and start with 'gAAAAAB'
    decrypted = decrypt(invalid_cipher)
    
    assert decrypted is None, "Decryption of an invalid token should return None"

def test_decrypt_empty_string():
    encrypted = encrypt("")
    decrypted = decrypt(encrypted)

    assert isinstance(encrypted, str), "Encrypted value should be a string even for empty input"
    assert len(encrypted) > 20, "Encrypted value should still be significantly longer than the plaintext (which is empty)"
    assert decrypted == "", "Decrypted value of an encrypted empty string should be an empty string"

def test_encrypt_empty_input():
    encrypted = encrypt(None)
    decrypted = decrypt(encrypted)

    assert encrypted == "", "Encrypting None should return an empty string"
    assert decrypted is None, "Decrypting an empty string should return None"