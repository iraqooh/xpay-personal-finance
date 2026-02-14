from .database import db_session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from uuid import UUID

from .models import User, Transaction, Category

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
if not SECRET_KEY:
    raise ValueError("Missing SECRET KEY in the environment variables")

# Dependency to get a database session
def get_db():
    """
    Dependency function to provide a database session for request handlers. This function creates a new database session, yields it to the request handler, and ensures that the session is properly closed after the request is processed.
    """
    db = db_session()
    try:
        # Yield the database session to the request handler
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_category_or_404(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(404, "Category not found")
    if category.user_id and category.user_id != current_user.id:
        raise HTTPException(403, "Not owner")
    return category


def get_transaction_or_404(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.user_id != current_user.id:
        raise HTTPException(403, "Not owner")
    return tx