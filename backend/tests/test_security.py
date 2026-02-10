from app.core.security import *
from jose import jwt
from datetime import datetime, timedelta, timezone

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

def test_create_access_token_returns_string_and_empty_data_does_not_break_token():
    token = create_access_token(subject="user123", data=None)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 20
    assert decoded["sub"] == "user123" # Subject should be correctly encoded in the token

def test_token_contains_subject_expiration_claim_and_issued_at():
    subject = "user456"
    token = create_access_token(subject=subject, data=None)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == subject
    assert "exp" in decoded
    assert "iat" in decoded

def test_token_contains_additional_payload_data():
    subject = "user789"
    additional_data = {"role": "admin", "permissions": ["read", "write"]}
    token = create_access_token(subject=subject, data=additional_data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == subject
    assert decoded["role"] == "admin"
    assert decoded["permissions"] == ["read", "write"]

def test_token_respects_custom_expiration_time():
    custom_expiry = timedelta(minutes=5)
    token = create_access_token(
        subject="user000", 
        data=None, 
        expires_delta=custom_expiry
    )
    
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    exp_timestamp = decoded["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    now = datetime.now(timezone.utc)

    assert exp_datetime > now
    assert exp_datetime <= now + custom_expiry + timedelta(seconds=5) # Allow a small buffer for processing time

def test_tokens_generated_twice_are_different():
    subject = "user111"
    token1 = create_access_token(subject=subject, data=None)
    from time import sleep
    sleep(3) # Ensure a different issued at time for the second token
    token2 = create_access_token(subject=subject, data=None)

    assert token1 != token2 # Each call should generate a unique token due to different issued at times