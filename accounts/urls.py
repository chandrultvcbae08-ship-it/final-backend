from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterPatientView,
    RegisterDoctorView,
    LoginView,
    LogoutView,
    UserProfileView,
    DeleteAccountView
)

urlpatterns = [
    path('register/patient/', RegisterPatientView.as_view(), name='register-patient'),
    path('register/doctor/', RegisterDoctorView.as_view(), name='register-doctor'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
