from app.core.security import *

def test_password_hashing():
    password = "MySecurePassword123!"

    hashed = get_password_hash(password)

    assert hashed is not None # Ensure we got a hash back
    assert isinstance(hashed, str) # Hash should be a string
    assert len(hashed) > 20 # bcrypt hashes are typically around 60 characters
    assert hashed != password # Hash should not be the same as the plaintext password
    assert hashed.startswith("$argon2") # Argon2 hashes start with $argon2
    assert hashed != get_password_hash(password) # Hashing the same password should produce different hashes due to salt

def test_password_verification_correct():
    password = "Test!@#456pass"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True # Correct password should verify

def test_password_verification_incorrect():
    password = "CorrectPass789"
    wrong_password = "WrongPass789"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False # Incorrect password should not verify

def test_different_hashes_for_same_password():
    password = "PasswordOne!@#"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2 # Hashes should be different due to random salt
    assert verify_password(password, hash1) # Both hashes should verify the same password
    assert verify_password(password, hash2)