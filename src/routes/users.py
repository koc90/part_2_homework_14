from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.model import User
from src.repository import auth as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb, UserAvatar

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> User:
    """
    Retrieve the current user's information.

    :param current_user: The current user making the request.
    :type current_user: User
    :return: The current user's information.
    :rtype: User
    """
    print("in routes.users.read_users_me")
    return current_user


@router.patch("/avatar", response_model=UserAvatar)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """
    Update the current user's avatar.

    :param file: The image file to upload as avatar.
    :type file: UploadFile
    :param current_user: The current user making the request.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: Updated current user's avatar.
    :rtype: User
    """
    print("in routes.users.update_avatar_user")
    cloudinary.config(
        cloud_name=settings.cloud_name,
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.email}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"ContactsApp/{current_user.email}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
