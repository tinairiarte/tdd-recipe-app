from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# To run
# docker-compose run --rm app sh -c "python manage.py test user"

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'test@tina.be',
            'password': 'tina_secret',
            'name': 'No Supro'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # We expect 200 response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # We expect User object to be created
        # **res.data is dict response
        # it includes payload + _id
        user = get_user_model().objects.get(**res.data)
        self.assertIsNotNone(user)

        # We expect a valid encrypted password is also created
        self.assertTrue(user.check_password(payload['password']))
        # We expect the password not be available through user object
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        payload = {
            'email': 'test@tina.be',
            'password': 'tina_secret',
            'name': 'No Supro'
        }

        # We expect User object to be created
        create_user(**payload)

        # We expect NO Identical User object to be created
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Password should be more than 5 characters """
        payload = {
            'email': 'test@tina.be',
            'password': 'tina',
            'name': 'No Supro'
        }

        # We expect NO short password User object to be created
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # We expect User not to be created
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            'email': 'test@tina.be',
            'password': 'tina',
            'name': 'No Supro'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        # assume 200 status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # asume token in response
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        payload = {
            'email': 'test@tina.be',
            'password': 'tina',
            'name': 'No Supro'
        }

        incorrect_payload = {
            'email': 'test@tina.be',
            'password': 'wrong password',
            'name': 'No Supro'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, incorrect_payload)

        # assume 200 status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # asume token not in response
        self.assertNotIn('token', res.data)

    def test_no_token_if_no_user(self):
        payload = {
            'email': 'test@tina.be',
            'password': 'tina',
            'name': 'No Supro'
        }

        res = self.client.post(TOKEN_URL, payload)

        # assume 200 status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # asume token not in response
        self.assertNotIn('token', res.data)

    def test_no_token_if_missing_fields(self):
        payload = {
            'email': 'test@tina.be',
            'password': '',
            'name': 'No Supro'
        }

        res = self.client.post(TOKEN_URL, payload)

        # assume 200 status code
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # asume token not in response
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUSerApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@tina.be',
            password='tina_secret',
            name='No Supro'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_no_http_post_me_allowed(self):
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
