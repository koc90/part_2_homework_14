from datetime import datetime, timedelta

from fastapi import status, HTTPException

from ..database.model import Contact


def get_id_birthday_upcoming(dates_id_list: list[tuple[datetime, int]]) -> list[int]:
    """
    Retrieves IDs of contacts whose birthdays are upcoming within the next 7 days.

    :param dates_id_list: A list of tuples where each tuple contains a datetime object representing the contact's birthday and an integer representing the contact's ID.
    :type dates_id_list: List[tuple[datetime, int]]

    :return: A list of contact IDs whose birthdays are upcoming within the next 7 days.
    :rtype: List[int]
    """

    print("We are in get_id_birthady_upcoming")

    id_list = []

    today = datetime.now().date()
    this_year = today.year
    days = timedelta(days=7)

    for date_tuple in dates_id_list:
        born_date = date_tuple[0].date()
        contact_id = date_tuple[1]
        born_day = born_date.day
        born_month = born_date.month

        closest_birthday = datetime(
            year=this_year, month=born_month, day=born_day
        ).date()

        if closest_birthday < today:
            closest_birthday = datetime(
                year=this_year + 1, month=born_month, day=born_day
            ).date()

        if closest_birthday - today <= days:
            id_list.append(contact_id)

    return id_list


def get_no_contacts_exception(contacts: Contact | list[Contact]):
    """
    Raises an HTTPException with a 404 status code and "No contact found" detail if the contacts list is empty.

    :param contacts: Simple contact or list of contacts.
    :type contacts: Contact or list[Contact]

    :raises HTTPException: Exception with a 404 status code and "No contact found" detail if contact is None or empty list.
    """
    print("We are in get_no_contact_exeption")

    if bool(contacts) == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contact found"
        )
