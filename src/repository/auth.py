from sqlalchemy.orm import Session
from src.database.model import User
from src.schemas import UserModel

import logging

logging.basicConfig(level=logging.ERROR)


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database by email.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email, or None if not found.
    :rtype: User | None
    """
    ...
    logging.debug("in repo.auth.get_user_by_email")

    user = db.query(User).filter(User.email == email).first()
    return user


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    :param body: The data for the new user.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    logging.debug("in repo.auth.create_user")

    new_user = User(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a user in the database.

    :param user: The user to update the token for.
    :type user: User
    :param token: The new refresh token, or None.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    """
    logging.debug("in repo.auth.update_token")
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    """
    Confirms the email address of a user in the database.

    :param email: The email address to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    """
    logging.debug("in repo.auth.confirmed_email")
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates the avatar URL for a user in the database.

    :param email: The email address of the user.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The user with the updated avatar URL.
    :rtype: User
    """
    logging.debug("in repo.auth.update_avatar")
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
