from pydantic import BaseModel, Field, PastDate


class ContactBase(BaseModel):
    """
    Schema representing the base structure of a contact.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        born_date (PastDate): The birth date of the contact, must be in the past.
        additional (str): Additional information about the contact.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    phone: str = Field(max_length=15)
    born_date: PastDate
    additional: str = Field(max_length=200)


class ContactResponse(ContactBase):
    """
    Schema representing the response structure for a contact.

    Inherits:
        ContactBase: Base structure of a contact.

    Attributes:
        id (int): The ID of the contact.
    """

    id: int

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    """
    Schema representing the structure of a user model.

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    email: str = Field(max_length=50)
    password: str = Field(max_length=255)


class UserBase(BaseModel):
    """
    Schema representing the base structure of a user.

    Attributes:
        email (str): The email address of the user.
    """

    email: str = Field(max_length=50)

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
    Schema representing the response structure for a user.

    Attributes:
        user (UserBase): Base structure of a user.
        detail (str): Information message indicating user creation success.
    """

    user: UserBase
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Schema representing the structure of a token.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The token type (default is "bearer").
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Schema representing the structure of a request email.

    Attributes:
        email (str): The email address.
    """

    email: str = Field(max_length=50)


class UserDb(BaseModel):
    """
    Schema representing the structure of a user from the database.

    Attributes:
        id (int): The ID of the user.
        email (str): The email address of the user.
        avatar (str | None): The avatar URL of the user, or None if not available.
    """

    id: int
    email: str
    avatar: str | None

    class Config:
        orm_mode = True


class UserAvatar(BaseModel):
    """
    Schema representing the structure of a user avatar.

    Attributes:
        avatar (str): The avatar URL of the user.
    """

    avatar: str

    class Config:
        orm_mode = True
