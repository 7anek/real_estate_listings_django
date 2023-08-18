from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import SignIn, SignOut, SignUp, EmailConfirmationView, EmailConfirmationSuccessView, EmailConfirmationFailureView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)


app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='token_register'),
    path('signin/', SignIn.as_view(), name='token_obtain_pair'),
    path('signin/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signout/', SignOut.as_view(), name='token_blacklist'),
    path('confirm-email/<uuid:token>/', EmailConfirmationView.as_view(), name='email_confirmation'),
    path('email-confirmation/success/<int:user_id>/', EmailConfirmationSuccessView.as_view(), name='email_confirmation_success'),
    path('email-confirmation/failure/<uuid:token>/', EmailConfirmationFailureView.as_view(), name='email_confirmation_failure'),

]