from django.urls import path
from .views import (
    PrescriptionListCreateView,
    PrescriptionDetailView,
    PrescriptionByAppointmentView
)

urlpatterns = [
    path('', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('<int:pk>/', PrescriptionDetailView.as_view(), name='prescription-detail'),
    path('appointment/<int:appointment_id>/', PrescriptionByAppointmentView.as_view(), name='prescription-by-appointment'),
]
