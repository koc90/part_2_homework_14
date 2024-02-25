import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from random import randint
from datetime import datetime

from src.database.model import User
from src.schemas import UserModel
from src.repository.auth import *


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User()

    async def test_get_user_by_email(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email="text", db=self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserModel(email="text", password="text")
        result = await create_user(body=body, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.email, body.email)

    async def test_update_token(self):
        token = "token"
        await update_token(self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirm_email(self):
        self.session.query().filter().first.return_value = self.user
        await confirm_email(email="text", db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        avatar = "avatar"
        result = await update_avatar(email="text", url=avatar, db=self.session)
        self.assertEqual(self.user, result)
        self.assertEqual(self.user.avatar, avatar)
