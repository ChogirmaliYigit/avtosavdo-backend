from django.urls import path
from users.views import UpdateUserDataView, UserLoginView

urlpatterns = [
    path("auth", UserLoginView.as_view(), name="sign-in"),
    path("update/<int:telegram_id>", UpdateUserDataView.as_view(), name="update-data"),
]
