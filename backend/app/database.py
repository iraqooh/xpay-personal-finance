from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create the SQLAlchemy engine
db_engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL query logging for debugging
    pool_pre_ping=True, # Enable connection pool pre-ping to check if connections are alive
    pool_size=10,  # Set the connection pool size
    max_overflow=20,  # Allow overflow of connections beyond the pool size
)

# Create a configured "Session" class
db_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=db_engine
)