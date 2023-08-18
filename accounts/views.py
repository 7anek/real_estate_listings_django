from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import APIException, ValidationError, NotFound
from django.contrib.auth import get_user_model
User = get_user_model()
from properties_scrapy.utils import generate_url
from django.conf import settings
from django.core.mail import send_mail
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework import viewsets, status
import os
from django.http import HttpResponseRedirect

# Create your views here.
class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        first_name = request.data["first_name"] if "first_name" in request.data else ""
        last_name = request.data["last_name"] if "last_name" in request.data else ""
        if "email" in request.data:
            email = request.data["email"]
        else:
            raise ValidationError("The given email must be set")
        if "username" in request.data:
            username = request.data["username"]
        else:
            raise ValidationError("The given username must be set")
        password = request.data["password"] if "password" in request.data else ""
        try:
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password, is_staff=False, is_superuser=False, is_active=False)
            confirmation_token = uuid.uuid4()
            user.confirmation_token = confirmation_token
            user.save()

            # confirmation_link = f"https://{settings.HOST_URL}/confirm-email/?token={confirmation_token}"
            # confirmation_link = f"{settings.HOST_URL}/confirm-email/?token={confirmation_token}"
            confirmation_link = generate_url(scheme=settings.HOST_SCHEME, netloc=settings.HOST_URL,
                                             path=reverse('accounts:email_confirmation', kwargs={"token": confirmation_token}))
            send_mail(
                "Potwierdzenie Emaila",
                f"Kliknij w poniższy link, aby potwierdzić swój email: {confirmation_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            raise APIException(str(e))
            # return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("User created")


class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password", "")

        if not email:
            raise ValidationError("Email field is required.")
        if not username:
            raise ValidationError("Username field is required.")
        if not password:
            raise ValidationError("Password field is required.")

        try:
            existing_user = User.objects.filter(username=username, email=email, is_active=False,
                                                confirmation_token__isnull=False).first()
            if existing_user:
                existing_user.confirmation_token = uuid.uuid4()
                existing_user.save()
                confirmation_link = generate_url(scheme=settings.HOST_SCHEME, netloc=settings.HOST_URL,
                                                 path=reverse('accounts:email_confirmation',
                                                 kwargs={"token": existing_user.confirmation_token}))
                send_mail(
                    "Potwierdzenie Emaila",
                    f"Kliknij w poniższy link, aby potwierdzić swój email: {confirmation_link}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response("User with this username/email already exists. New confirmation link sent.")

            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password, is_staff=False, is_superuser=False, is_active=False)
            user.confirmation_token = uuid.uuid4()
            user.save()

            confirmation_link = generate_url(scheme=settings.HOST_SCHEME, netloc=settings.HOST_URL,
                                             path=reverse('accounts:email_confirmation',
                                             kwargs={"token": user.confirmation_token}))
            send_mail(
                "Potwierdzenie Emaila",
                f"Kliknij w poniższy link, aby potwierdzić swój email: {confirmation_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            raise APIException(str(e))

        return Response("User created", status=status.HTTP_201_CREATED)


class SignIn(TokenObtainPairView):
    permission_classes = [AllowAny]



class SignOut(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print('SignOut view')
        token = request.data["refresh"]
        if not token:
            print('not token')
            return Response("refresh token is empty", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            refresh_token = RefreshToken(token)
        except Exception as e:
            print(str(e))
            # raise APIException(str(e))
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print('adding token to blacklist')
        refresh_token.blacklist()
        return Response("OK")


class EmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user = User.objects.get(confirmation_token=token)
            user.is_active = True
            user.is_verified = True
            user.confirmation_token = None
            user.save()
            return redirect(reverse('accounts:email_confirmation_success', kwargs={'user_id': user.id}))
        except User.DoesNotExist:
            return redirect(reverse('accounts:email_confirmation_failure', kwargs={'token': token}))


class EmailConfirmationSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")

        # response_data = {
        #     "message": f"Email {user.email} confirmed",
        #     "redirect_url": f"{settings.HOST_SCHEME}://{os.environ['FRONTEND_URL']}/email-confirmation-success",
        #     "email": user.email,
        # }
        # return Response(response_data, status=status.HTTP_200_OK)
        redirect_url=f"{settings.HOST_SCHEME}://{os.environ['FRONTEND_URL']}/email-confirmation-success/{user.email}"
        return HttpResponseRedirect(redirect_to=redirect_url)


class EmailConfirmationFailureView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        redirect_url = f"{settings.HOST_SCHEME}://{os.environ['FRONTEND_URL']}/email-confirmation-failure"
        # return redirect(redirect_url)
        return HttpResponseRedirect(redirect_to=redirect_url)
        # return Response({"message": "Email confirmation failed"}, status=status.HTTP_400_BAD_REQUEST)
