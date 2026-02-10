from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from typing import Any, Optional
from jose import jwt

# Password hashing context configuration
# Using bcrypt for secure password hashing with automatic handling of salt and work factor
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a plaintext password using the configured password hashing context."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

load_dotenv()  # Load environment variables from .env file
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def create_access_token(
    subject: Any, # The subject can be any data that identifies the user (e.g., user ID or email)
    data: Optional[dict], # Additional data to include in the token payload (e.g., user roles, permissions)
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token with the given data and expiration time."""
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
