from typing import List

from sqlalchemy.orm import Session

from src.database.model import Contact, User
from src.schemas import ContactBase

from src.services.added_features import get_id_birthday_upcoming

import logging


async def get_contacts(db: Session, user: User) -> List[Contact]:
    """
    Retrieves all contacts belonging to a specific user from the database.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :return: A list of contacts belonging to the user.
    :rtype: List[Contact]
    """

    # return db.query(Contact).filter(Contact.user_id == user.id).first()
    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact(contact_id: int, db: Session, user: User) -> Contact:
    """
    Retrieves a specific contact by its ID belonging to a specific user from the database.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param user: The user whose contact is being retrieved.
    :type user: User
    :return: The contact with the specified ID belonging to the user.
    :rtype: Contact
    """
    logging.debug("We are in repo.get_contact function")
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user.id)
        .first()
    )
    return contact


async def get_contact_by_id(contact_id: str, db: Session, user: User) -> List[Contact]:
    """
    Retrieves a contact by its ID belonging to a specific user from the database.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: str
    :param db: The database session.
    :type db: Session
    :param user: The user whose contact is being retrieved.
    :type user: User
    :return: A list containing the contact with the specified ID belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("We are in repo.get_contact_by_id function")
    try:
        contact_id = int(contact_id)
    except:
        logging.error("ValueError: Contact_id must be an integer")
        return None
    else:
        return (
            db.query(Contact)
            .filter(Contact.id == contact_id, Contact.user_id == user.id)
            .all()
        )


async def get_contacts_by_first_name(
    contact_first_name: str, db: Session, user: User
) -> List[Contact]:
    """
    Retrieves contacts by their first name belonging to a specific user from the database.

    :param contact_first_name: The first name of the contacts to retrieve.
    :type contact_first_name: str
    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :return: A list of contacts with the specified first name belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("We are in repo.get_contact_by_first_name function")
    contacts = (
        db.query(Contact)
        .filter(Contact.first_name == contact_first_name, Contact.user_id == user.id)
        .all()
    )
    return contacts


async def get_contacts_by_last_name(
    contact_last_name: str, db: Session, user: User
) -> List[Contact]:
    """
    Retrieves contacts by their last name belonging to a specific user from the database.

    :param contact_last_name: The last name of the contacts to retrieve.
    :type contact_last_name: str
    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :return: A list of contacts with the specified last name belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("We are in repo.get_contact_by_last_name function")
    return (
        db.query(Contact)
        .filter(Contact.last_name == contact_last_name, Contact.user_id == user.id)
        .all()
    )


async def get_contact_by_email(
    contact_email: str, db: Session, user: User
) -> List[Contact]:
    """
    Retrieves a contact by its email address belonging to a specific user from the database.

    :param contact_email: The email address of the contact to retrieve.
    :type contact_email: str
    :param db: The database session.
    :type db: Session
    :param user: The user whose contact is being retrieved.
    :type user: User
    :return: A list containing the contact with the specified email address belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("in repo.get_contact_by_email function")
    return (
        db.query(Contact)
        .filter(Contact.email == contact_email, Contact.user_id == user.id)
        .all()
    )


async def get_contacts_by(
    field: str, value: str, db: Session, user: User
) -> List[Contact]:
    """
    Retrieves contacts by a specified field and value belonging to a specific user from the database.

    :param field: The field to filter the contacts by (e.g., "id", "first_name", "last_name", "email").
    :type field: str
    :param value: The value to filter the contacts by.
    :type value: str
    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :return: A list of contacts filtered by the specified field and value belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("in repo.get_contacts_by function")

    fields = {
        "id": get_contact_by_id,
        "first_name": get_contacts_by_first_name,
        "last_name": get_contacts_by_last_name,
        "email": get_contact_by_email,
    }

    if field in fields.keys():
        contacts = await fields[field](value, db, user)
    else:
        logging.error("There is no such field")
        contacts = []

    return contacts


async def create_new_contact(body: ContactBase, db: Session, user: User) -> Contact:
    """
    Creates a new contact for a specific user in the database.

    :param body: The data for the new contact.
    :type body: ContactBase
    :param db: The database session.
    :type db: Session
    :param user: The user for whom the contact is being created.
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    """
    logging.debug("in repo.create_new_contact function")
    contact = Contact(
        first_name=body.first_name.lower(),
        last_name=body.last_name.lower(),
        email=body.email.lower(),
        phone=body.phone,
        born_date=body.born_date,
        additional=body.additional.lower(),
        user_id=user.id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact: Contact, body: ContactBase, db: Session) -> Contact:
    """
    Updates an existing contact in the database.

    :param contact: The contact to update.
    :type contact: Contact
    :param body: The updated data for the contact.
    :type body: ContactBase
    :param db: The database session.
    :type db: Session
    """
    logging.debug("in repo.update_contact function")

    if contact:
        contact.first_name = body.first_name.lower()
        contact.last_name = body.last_name.lower()
        contact.email = body.email.lower()
        contact.phone = body.phone
        contact.born_date = body.born_date
        contact.additional = body.additional.lower()

        db.commit()
    return contact


async def remove_contact(contact: Contact, db: Session) -> Contact:
    """
    Removes an existing contact from the database.

    :param contact: The contact to remove.
    :type contact: Contact
    :param db: The database session.
    :type db: Session
    """
    logging.debug("in repo.remove_contact function")
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts_with_upcoming_birtday(db: Session, user: User) -> list[Contact]:
    """
    Retrieves contacts with upcoming birthdays for a specific user from the database.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being retrieved.
    :type user: User
    :return: A list of contacts with upcoming birthdays belonging to the user.
    :rtype: List[Contact]
    """
    logging.debug("in repo.get_contact_with_upcoming_birtday function")

    born_dates = db.query(Contact).values(Contact.born_date, Contact.id)

    id_list = get_id_birthday_upcoming(born_dates)
    contacts = (
        db.query(Contact)
        .filter(Contact.id.in_(id_list), Contact.user_id == user.id)
        .all()
    )

    return contacts
