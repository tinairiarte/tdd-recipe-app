from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = "mea2@gmail.com"
        password = "lkfbdlfldjfglkf"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = "mea2@gmaIl.cOm "
        normalized_email = "mea2@gmail.com"

        user = get_user_model().objects.create_user(
            email=email,
            password="randompassword"
        )

        self.assertEqual(user.email, normalized_email)

    def test_new_user_invalid_email(self):
        from django.core.exceptions import ValidationError

        invalid_emails = ["mea2@gmaIlcOm ", "mea2gmail.com", " "]

        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                user = get_user_model().objects.create_user(
                    email=email,
                    password="randompassword"
                )

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            email="mea2@gmail.com",
            password="randompassword"
        )

        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
