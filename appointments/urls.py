from django.urls import path
from .views import (
    SlotListCreateView,
    SlotDetailView,
    BookAppointmentView,
    AppointmentListView,
    AppointmentDetailView,
    CancelAppointmentView,
    UpdateAppointmentStatusView
)

urlpatterns = [
    path('slots/', SlotListCreateView.as_view(), name='slot-list-create'),
    path('slots/<int:pk>/', SlotDetailView.as_view(), name='slot-detail'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('', AppointmentListView.as_view(), name='appointment-list'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<int:pk>/cancel/', CancelAppointmentView.as_view(), name='appointment-cancel'),
    path('<int:pk>/status/', UpdateAppointmentStatusView.as_view(), name='appointment-update-status'),
]
