from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Optional
from jose import jwt
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Password hashing context configuration
# Using argon2 for secure password hashing with automatic handling of salt and work factor
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using the configured password hashing algorithm (argon2).
    
    :param password: The plaintext password to be hashed.
    :type password: str
    :return: The hashed password as a string.
    :rtype: str
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password using the configured password hashing algorithm (argon2).
    
    :param plain_password: The plaintext password to verify.
    :type plain_password: str
    :param hashed_password: The hashed password to compare against.
    :type hashed_password: str
    :return: True if the password is correct, False otherwise.
    :rtype: bool
    """
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set. Please set it in the .env file.")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def create_access_token(
    subject: Any, # The subject can be any data that identifies the user (e.g., user ID or email)
    data: Optional[dict] = None, # Additional data to include in the token payload (e.g., user roles, permissions)
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with the given subject, additional data, and expiration time.
    
    :param subject: The subject of the token, typically a unique identifier for the user (e.g., user ID or email).
    :type subject: Any
    :param data: Additional data to include in the token payload, such as user roles or permissions. This will be merged with standard claims.
    :type data: Optional[dict]
    :param expires_delta: The time duration after which the token should expire. If not provided, a default expiration time will be used.
    :type expires_delta: Optional[timedelta]
    :return: The encoded JWT access token as a string.
    :rtype: str
    """
    # If no additional data is provided, initialize it as an empty dictionary
    if data is None:
        data = {}
    
    # Calculate the expiration time for the token
    expire_minutes = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expire_minutes

    to_encode = data.copy()
    # Update the token payload with standard claims: subject (sub), expiration time (exp), and issued at time (iat)
    to_encode.update({
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }) 
    # Encode the token using the SECRET_KEY and ALGORITHM
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

