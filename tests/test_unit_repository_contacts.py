import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from random import randint
from datetime import datetime

from src.database.model import Contact, User
from src.schemas import ContactBase
from src.repository.contacts import *


class TestContacts(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):

        cls.funcs_by_field = [
            get_contact_by_id,
            get_contacts_by_first_name,
            get_contacts_by_last_name,
            get_contact_by_email,
        ]
        cls.existing_fields = ["id", "first_name", "last_name", "email"]
        cls.valid_values = ["1", "aaa", "bbb", "aaabbb@ccc.com"]

        cls.contact_base = {
            "first_name": "text",
            "last_name": "text",
            "email": "text",
            "phone": "text",
            "born_date": datetime(year=1998, month=12, day=5),
            "additional": "text",
        }

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User()
        self.contact = Contact()
        self.list_of_contact = [Contact()]
        self.list_of_contacts = [Contact() for _ in range(randint(1, 5))]

    async def auxiliary_fun_get_contacts(self, expected_result):
        self.session.query().filter().all.return_value = expected_result
        result = await get_contacts(db=self.session, user=self.user)
        self.assertEqual(result, expected_result)

    async def test_get_contacts(self):
        await self.auxiliary_fun_get_contacts(expected_result=self.list_of_contacts)

    async def test_get_contacts_empty(self):
        await self.auxiliary_fun_get_contacts([])

    async def auxiliary_fun_get_contact(self, expected_result):
        self.session.query().filter().first.return_value = expected_result
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, expected_result)

    async def test_get_contact_found(self):
        await self.auxiliary_fun_get_contact(expected_result=self.contact)

    async def test_get_contact_not_found(self):
        await self.auxiliary_fun_get_contact(expected_result=None)

    async def auxiliary_fun_get_contact_by_field(self, expected_result):
        self.session.query().filter().all.return_value = expected_result
        for arg, func in list(zip(self.valid_values, self.funcs_by_field)):
            result = await func(arg, db=self.session, user=self.user)
            self.assertEqual(result, expected_result)

    async def test_get_contact_by_field_found(self):
        await self.auxiliary_fun_get_contact_by_field(
            expected_result=self.list_of_contact
        )

    async def test_get_contact_by_field_not_found(self):
        await self.auxiliary_fun_get_contact_by_field(expected_result=[])

    async def test_get_contact_by_id_exception(self):
        await get_contact_by_id(contact_id="text", db=self.session, user=self.user)
        self.assertRaises(Exception)

    async def auxiliary_fun_get_contacts_by(self, expected_result):
        self.session.query().filter().all.return_value = expected_result
        for existing_field, valid_value in list(
            zip(self.existing_fields, self.valid_values)
        ):
            result = await get_contacts_by(
                field=existing_field, value=valid_value, db=self.session, user=self.user
            )
            self.assertEqual(result, expected_result)

    async def test_get_contacts_by_existing_field(self):
        await self.auxiliary_fun_get_contacts_by(expected_result=self.list_of_contact)

    async def test_get_contacts_by_not_existing_field(self):
        await self.auxiliary_fun_get_contacts_by(expected_result=[])

    def auxiliary_fun_to_compare(self, body: ContactBase, result: Contact):
        self.assertEqual(result.first_name, body.first_name.lower())
        self.assertEqual(result.last_name, body.last_name.lower())
        self.assertEqual(result.email, body.email.lower())
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.born_date, body.born_date)
        self.assertEqual(result.additional, body.additional.lower())

    async def test_create_new_contact(self):

        body = ContactBase(**self.contact_base)
        result = await create_new_contact(body=body, db=self.session, user=self.user)
        self.assertTrue(hasattr(result, "id"))
        self.auxiliary_fun_to_compare(body=body, result=result)

    async def test_uptade_contact(self):

        body = ContactBase(**self.contact_base)
        result = await update_contact(contact=self.contact, body=body, db=self.session)
        self.auxiliary_fun_to_compare(body=body, result=result)
        self.auxiliary_fun_to_compare(body=body, result=self.contact)

    async def test_remove_contact(self):
        result = await remove_contact(contact=self.contact, db=self.session)
        self.assertEqual(result, self.contact)

    async def test_birthady(self):
        self.session.query().values().return_value = []
        self.session.query().filter().all.return_value = self.list_of_contacts
        result = await get_contacts_with_upcoming_birtday(
            db=self.session, user=self.user
        )
        self.assertEqual(result, self.list_of_contacts)
