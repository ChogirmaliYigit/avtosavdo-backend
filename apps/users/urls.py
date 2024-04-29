from django.urls import path
from users.views import UserLoginView, UserRegistrationView

urlpatterns = [
    path("sign-up", UserRegistrationView.as_view(), name="sign-up"),
    path("sign-in", UserLoginView.as_view(), name="sign-in"),
]
