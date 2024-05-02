from django.urls import path
from users.views import UserLoginView

urlpatterns = [
    path("auth", UserLoginView.as_view(), name="sign-in"),
]
