from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from ..schemas import UserCreate, AuthResponse, UserRead
from ..dependencies import get_db
from ..models import User
from ..core.security import get_password_hash, verify_password
from ..core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return an access token if the registration is successful.

    :param user: The user registration data, including email, full name, and password. This is typically sent as a JSON payload in the request body.
    :type user: UserCreate
    :param db: The database session dependency that provides access to the database for querying and creating user information. This is typically injected using FastAPI's dependency injection system.
    :type db: Session
    """
    # Check if the email is already registered
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        # Create a new user
        new_user = User(
            email=user.email, 
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name
        )
        
        # Save the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    access_token = create_access_token(subject=str(new_user.id))

    return {
        "user": UserRead.model_validate(new_user),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token if the credentials are valid.
    
    :param form_data: The form data containing the email and password for authentication. This is typically sent as a form-encoded request with fields "username" and "password".
    :type form_data: OAuth2PasswordRequestForm
    :param db: The database session dependency that provides access to the database for querying user information. This is typically injected using FastAPI's dependency injection system.
    :type db: Session
    """
    # Authenticate the user by verifying the email and password
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create an access token for the authenticated user
    access_token = create_access_token(subject=str(user.id))

    return {
        "user": UserRead.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }