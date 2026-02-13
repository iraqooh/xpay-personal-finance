from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from fastapi.responses import RedirectResponse

from app.core.oauth import oauth_client
from app.dependencies import get_db
from app.models import User
from app.core.security import create_access_token

router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate the Google OAuth login flow by redirecting the user to Google's authorization endpoint.
    
    :param request: The incoming HTTP request object, used to generate the redirect URI for the OAuth flow.
    :type request: Request
    """
    redirect_uri = request.url_for("google_callback")
    print("Redirect URI:", redirect_uri)
    return await oauth_client.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle the callback from Google after the user has been authenticated. This endpoint processes the authorization response,
    retrieves the user's information, and creates or updates the user in the database.
    
    :param request: The incoming HTTP request object, used to process the OAuth callback.
    :type request: Request
    :param db: The database session, injected as a dependency for database operations.
    :type db: Session
    """
    try:
        token = await oauth_client.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authorize with Google"
        )
    
    userinfo: dict[str, Any] = await oauth_client.google.userinfo(token=token)

    email = userinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account does not have an email address"
        )
    
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # If the user does not exist, create a new user record in the database
        if not userinfo.get("name"):
            userinfo["name"] = "Unknown Google User"
        
        user = User(
            email=email,
            full_name=userinfo.get("name"),
            # profile_picture=userinfo.get("picture")
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user) # Refresh the user instance to get the generated ID and other fields from the database
    
    access_token = create_access_token(
        subject=user.id,
        data={"email": user.email, "full_name": user.full_name}
    )
    redirect_url = f"/?access_token={access_token}" # Redirect to the frontend with the access token as a query parameter

    return RedirectResponse(url=redirect_url)