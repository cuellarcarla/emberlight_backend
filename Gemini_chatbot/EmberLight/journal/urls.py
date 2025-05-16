from django.urls import path
from .views import JournalEntryListCreate, JournalEntryRetrieveUpdate

urlpatterns = [
    path('entries/', JournalEntryListCreate.as_view(), name='journal-entries'),
    path('entries/<int:pk>/', JournalEntryRetrieveUpdate.as_view(), name='journal-entry-detail'),
]