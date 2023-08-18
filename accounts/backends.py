from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailorUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        # Sprawdź, czy istnieje użytkownik o danym username lub email
        user = User.objects.filter(username=username) | User.objects.filter(email=username)
        user = user.first()

        if user and user.check_password(password):
            if user.confirmation_token:
                return None
            return user
        return None