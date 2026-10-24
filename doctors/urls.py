from django.urls import path
from .views import (
    DoctorListView,
    DoctorDetailView,
    DoctorProfileUpdateView,
    DoctorSpecializationsView
)

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('specializations/', DoctorSpecializationsView.as_view(), name='doctor-specializations'),
    path('profile/', DoctorProfileUpdateView.as_view(), name='doctor-my-profile'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
]
