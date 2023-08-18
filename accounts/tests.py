from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.test import APITestCase,APIRequestFactory, force_authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model

from accounts.views import EmailConfirmationSuccessView

User = get_user_model()

# Create your tests here.

class SignUpTestCase(APITestCase):
    def test_signup_without_username(self):
        response = self.client.post(reverse('accounts:token_register'), {'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data[0], 'The given username must be set')

    # def test_signup_user_creation_error(self):
    #     response = self.client.post('/signup/', {'username': 'john', 'password': 'password', 'email': ['invalid']})
    #     self.assertEqual(response.status_code, 500)
    #     self.assertEqual(response.data, 'User creation error')

    def test_signup_success(self):
        response = self.client.post(reverse('accounts:token_register'),
                                    {'username': 'john', 'password': 'password', 'email': 'valid@example.com'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'User created')

        # Verify that a User object was created with the correct attributes
        user = User.objects.get(username='john')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.email, 'valid@example.com')
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_user_signup_sends_email(self):
        data = {'username': 'john', 'password': 'password', 'email': 'valid@example.com'}
        response = self.client.post(reverse('accounts:token_register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Sprawdź, czy została wysłana dokładnie jedna wiadomość
        self.assertEqual(len(mail.outbox), 1)

        # Sprawdź zawartość wiadomości
        email = mail.outbox[0]
        self.assertIn('Potwierdzenie Emaila', email.subject)
        self.assertIn('Kliknij w poniższy link', email.body)
        self.assertEqual(email.from_email, settings.EMAIL_HOST_USER)
        self.assertEqual(email.to, [data['email']])

class EmailConfirmationViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="secret123",
            confirmation_token="testtoken"
        )

    def test_email_confirmation_success(self):
        response = self.client.get(reverse("accounts:email_confirmation"), {"token": "testtoken"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email confirmed successfully."})
        self.assertTrue(User.objects.get(username="johndoe").is_active)

    def test_email_confirmation_invalid_token(self):
        response = self.client.get(reverse("accounts:email_confirmation"), {"token": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Invalid confirmation token."})


class EmailConfirmationSuccessViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = EmailConfirmationSuccessView.as_view()

        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword', confirmation_token='testtoken'
        )

    def test_email_confirmation_success(self):
        # url = f'/confirm-email/{self.user.confirmation_token}/'
        url=reverse('accounts:email_confirmation', kwargs={'token':self.user.confirmation_token})
        request = self.factory.get(url)
        force_authenticate(request, user=self.user)  # Autentykacja użytkownika
        response = self.view(request, token=self.user.confirmation_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_email_confirmation_success_invalid_token(self):
        url = '/accounts/token/confirm-email/invalidtoken/'
        request = self.factory.get(url)
        response = self.view(request, token='invalidtoken')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn('message', response.data)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
class JWTokenTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='password')

    def test_signin_success(self):
        response = self.client.post(reverse('accounts:token_obtain_pair'), {'username': 'john', 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_signin_invalid_credentials(self):
        response = self.client.post(reverse('accounts:token_obtain_pair'), {'username': 'john', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        print('test_token_refresh_success')
        token = RefreshToken.for_user(self.user)
        response = self.client.post(reverse('accounts:token_refresh'), {'refresh': str(token)})
        print('response', response)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertNotEqual(token.access_token, response.data['access'])
        # Ręczne dodanie tokena odświeżania do blacklisty
        outstanding_token = OutstandingToken.objects.get(token=token)
        blacklisted_token = BlacklistedToken.objects.create(token=outstanding_token)

        # Sprawdzenie, czy odświeżony token został dodany do blacklisty
        # blacklisted_tokens = RefreshToken.objects.filter(token=token)
        blacklisted_tokens = BlacklistedToken.objects.filter(token=outstanding_token)
        self.assertTrue(blacklisted_tokens.exists())

    def test_token_refresh_empty_token(self):
        response = self.client.post(reverse('accounts:token_refresh'), {'refresh': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('refresh', response.data)

    def test_token_refresh_invalid_token(self):
        response = self.client.post(reverse('accounts:token_refresh'), {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

    def test_signout_success(self):
        token = RefreshToken.for_user(self.user)
        response = self.client.post(reverse('accounts:token_blacklist'), {'refresh': str(token)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'OK')
        # blacklisted_tokens = RefreshToken.objects.filter(token=token)
        blacklisted_tokens = BlacklistedToken.objects.filter(token__jti=token['jti'])
        self.assertTrue(blacklisted_tokens.exists())

    def test_signout_empty_token(self):
        response = self.client.post(reverse('accounts:token_blacklist'), {'refresh': ''})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'refresh token is empty')

    def test_signout_invalid_token(self):
        response = self.client.post(reverse('accounts:token_blacklist'), {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'Token is invalid or expired')
