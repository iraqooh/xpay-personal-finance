from passlib.context import CryptContext

# Password hashing context configuration
# Using bcrypt for secure password hashing with automatic handling of salt and work factor
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a plaintext password using the configured password hashing context."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)