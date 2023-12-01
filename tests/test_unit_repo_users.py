import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.database.models import User
from app.schemas import UserModel
from app.repo.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)

class TestUserFunctions(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock(spec=Session)

    def test_get_user_by_email(self):
        # TODO: Set up test data in your database
        email = "test@example.com"
        expected_user = User(id=1, email=email)
        self.db_session.query.return_value.filter.return_value.first.return_value = expected_user

        result = get_user_by_email(email, self.db_session)

        self.assertEqual(result, expected_user)

    @patch('libgravatar.Gravatar.get_image')
    def test_create_user(self, mock_get_image):
        # TODO: Set up test data and mock Gravatar
        email = "test@example.com"
        user_data = UserModel(email=email)
        mock_get_image.return_value = "mocked_avatar_url"

        created_user = create_user(user_data, self.db_session)

        self.assertIsInstance(created_user, User)
        self.assertEqual(created_user.email, email)
        self.assertEqual(created_user.avatar, "mocked_avatar_url")
        self.assertTrue(self.db_session.add.called)
        self.assertTrue(self.db_session.commit.called)
        self.assertTrue(self.db_session.refresh.called)

    def test_update_token(self):
        # TODO: Set up test data in your database
        user = User(id=1, email="test@example.com")
        new_token = "new_token"

        update_token(user, new_token, self.db_session)

        self.assertEqual(user.refresh_token, new_token)
        self.assertTrue(self.db_session.commit.called)

    def test_confirmed_email(self):
        # TODO: Set up test data in your database
        email = "test@example.com"
        user = User(id=1, email=email)
        self.db_session.query.return_value.filter.return_value.first.return_value = user

        confirmed_email(email, self.db_session)

        self.assertTrue(user.confirmed)
        self.assertTrue(self.db_session.commit.called)

    def test_update_avatar(self):
        # TODO: Set up test data in your database
        email = "test@example.com"
        user = User(id=1, email=email)
        new_avatar_url = "new_avatar_url"
        self.db_session.query.return_value.filter.return_value.first.return_value = user

        updated_user = update_avatar(email, new_avatar_url, self.db_session)

        self.assertEqual(updated_user.avatar, new_avatar_url)
        self.assertTrue(self.db_session.commit.called)


if __name__ == '__main__':
    unittest.main()
