from app.core.security import *
from jose import jwt
from datetime import datetime, timedelta, timezone

def test_password_hashing():
    """
    Test that hashing a password returns a valid hash string that is different from the plaintext password, and that hashing the same password multiple times produces different hashes due to salting.
     This ensures that the password hashing function is correctly implemented with proper salting, which is crucial for security to prevent rainbow table attacks and ensure that even if two users have the same password, their hashes will be different.
     The assertions check that the hash is a string, is of a reasonable length (bcrypt hashes are typically around 60 characters), is not the same as the plaintext password, starts with the expected prefix for Argon2 hashes, and that hashing the same password twice does not produce the same hash.
    """
    password = "MySecurePassword123!"

    hashed = get_password_hash(password)

    assert hashed is not None # Ensure we got a hash back
    assert isinstance(hashed, str) # Hash should be a string
    assert len(hashed) > 20 # bcrypt hashes are typically around 60 characters
    assert hashed != password # Hash should not be the same as the plaintext password
    assert hashed.startswith("$argon2") # Argon2 hashes start with $argon2
    assert hashed != get_password_hash(password) # Hashing the same password should produce different hashes due to salt

def test_password_verification_correct():
    """
    Test that verifying a correct plaintext password against its hashed version returns True, confirming that the password verification function correctly identifies valid passwords.
     This test ensures that the password verification function is working as intended by confirming that it returns True when the correct password is provided, which is essential for user authentication to function properly.
    """
    password = "Test!@#456pass"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True # Correct password should verify

def test_password_verification_incorrect():
    """
    Test that verifying an incorrect plaintext password against a hashed password returns False, confirming that the password verification function correctly identifies invalid passwords.
     This test ensures that the password verification function is working as intended by confirming that it returns False when an incorrect password is provided, which is essential for user authentication to prevent unauthorized access.
    """
    password = "CorrectPass789"
    wrong_password = "WrongPass789"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False # Incorrect password should not verify

def test_different_hashes_for_same_password():
    """
    Test that hashing the same plaintext password multiple times produces different hash outputs, confirming that the password hashing function uses proper salting to ensure unique hashes for the same input.
     This test is crucial for security, as it verifies that the hashing function incorporates a random salt, which prevents attackers from using precomputed hash tables (rainbow tables) to reverse-engineer passwords and ensures that even if two users have the same password, their stored hashes will be different.
    """
    password = "PasswordOne!@#"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2 # Hashes should be different due to random salt
    assert verify_password(password, hash1) # Both hashes should verify the same password
    assert verify_password(password, hash2)

def test_create_access_token_returns_string_and_empty_data_does_not_break_token():
    """
    Test that the create_access_token function returns a valid JWT token string, and that providing None for the additional data does not cause any issues in token creation.
     This test ensures that the create_access_token function is robust and can handle cases where no additional data is provided, while still generating a valid token that can be decoded to retrieve the subject claim.
     The assertions check that the returned token is a string, is of a reasonable length for a JWT token, and that the decoded token contains the correct subject claim, confirming that the token was created successfully even without additional data.
    """
    token = create_access_token(subject="user123", data=None)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 20
    assert decoded["sub"] == "user123" # Subject should be correctly encoded in the token

def test_token_contains_subject_expiration_claim_and_issued_at():
    """
    Test that the JWT token created by create_access_token contains the expected claims, including the subject (sub), expiration time (exp), and issued at time (iat).
     This test ensures that the create_access_token function is correctly including the necessary claims in the token payload, which are essential for token validation and authentication processes. The presence of the subject claim allows the application to identify the user associated with the token, while the expiration and issued at claims are crucial for managing token validity and preventing misuse.
     The assertions check that the decoded token contains the subject claim with the correct value, as well as the presence of the expiration and issued at claims, confirming that the token was created with the expected structure and information.
    """
    subject = "user456"
    token = create_access_token(subject=subject, data=None)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == subject
    assert "exp" in decoded
    assert "iat" in decoded

def test_token_contains_additional_payload_data():
    """
    Test that the JWT token created by create_access_token correctly includes additional payload data provided in the data parameter, and that this data can be retrieved from the decoded token.
     This test ensures that the create_access_token function is properly merging additional data into the token payload, which allows for the inclusion of custom claims such as user roles or permissions that can be used for authorization purposes in the application.
     The assertions check that the additional data provided (e.g., role and permissions) is present in the decoded token, confirming that the function correctly incorporates this data into the token payload and that it can be accessed after decoding the token.
    """
    subject = "user789"
    additional_data = {"role": "admin", "permissions": ["read", "write"]}
    token = create_access_token(subject=subject, data=additional_data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == subject
    assert decoded["role"] == "admin"
    assert decoded["permissions"] == ["read", "write"]

def test_token_respects_custom_expiration_time():
    """
    Test that the JWT token created by create_access_token respects a custom expiration time provided via the expires_delta parameter, and that the token's expiration claim is set accordingly.
     This test ensures that the create_access_token function correctly calculates the expiration time based on the provided expires_delta, which is important for managing token lifetimes and ensuring that tokens expire as expected to enhance security.
     The assertions check that the expiration time in the decoded token is greater than the current time and is within the expected range based on the custom expiration time provided, confirming that the function correctly handles custom expiration times when creating tokens.
    """
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
    """
    Test that generating a token for the same subject multiple times results in different token strings, confirming that the create_access_token function produces unique tokens even for the same input due to the inclusion of the issued at (iat) claim.
     This test ensures that the create_access_token function is not producing identical tokens for the same subject, which is important for security to prevent token replay attacks and to ensure that each token has a unique identifier based on its creation time.
     The assertion checks that two tokens generated for the same subject are not the same string, confirming that the function is correctly incorporating the issued at time to create unique tokens for each call.
    """
    subject = "user111"
    token1 = create_access_token(subject=subject, data=None)
    from time import sleep
    sleep(3) # Ensure a different issued at time for the second token
    token2 = create_access_token(subject=subject, data=None)

    assert token1 != token2 # Each call should generate a unique token due to different issued at times