from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from src.services.email import send_email
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import auth as repository_users
from src.services.auth import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Endpoint for user registration.

    :param body: The data for creating a new user.
    :type body: UserModel
    :param background_tasks: Background tasks to execute.
    :type background_tasks: BackgroundTasks
    :param request: The request object.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: Details about the newly created user.
    :rtype: dict
    """
    print("We are in routes.auth.signup")
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.email, request.base_url
    )
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    """
    Endpoint for user authentication and login.

    :param body: The login credentials.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: Session
    :return: Access and refresh tokens.
    :rtype: dict
    """
    print("We are in routes.auth.login")
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = auth_service.create_token(
        data={"sub": user.email}, token_type="access_token"
    )
    refresh_token = auth_service.create_token(
        data={"sub": user.email}, token_type="refresh_token"
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Endpoint for refreshing access token.

    :param credentials: The authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: Session
    :return: Refreshed access and refresh tokens.
    :rtype: dict
    """
    print("We are in routes.auth.refresh_token")
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_token(
        data={"sub": email}, token_type="access_token"
    )
    refresh_token = await auth_service.create_token(
        data={"sub": email}, token_type="refresh_token"
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirm_email/{token}")
async def confirm_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Endpoint for confirming user email.

    :param token: The confirmation token sent to the user's email.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: Confirmation message.
    :rtype: dict
    """
    print("We are in routes.auth.confirm_email")
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirm_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Endpoint for requesting email confirmation.

    :param body: The email address for which confirmation is requested.
    :type body: RequestEmail
    :param background_tasks: Background tasks to execute.
    :type background_tasks: BackgroundTasks
    :param request: The request object.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: Confirmation message.
    :rtype: dict
    """
    print("We are in routes.auth.request_email")
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.email, request.base_url)
    return {"message": "Check your email for confirmation."}
