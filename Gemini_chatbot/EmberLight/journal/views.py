from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import JournalEntry
from .serializers import JournalEntrySerializer
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

class JournalEntryListCreate(generics.ListCreateAPIView):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get entries from the last 30 days by default
        date_from = timezone.now().date() - timedelta(days=30)
        return JournalEntry.objects.filter(
            user=self.request.user,
            date__gte=date_from
        ).order_by('-date')

    def create(self, request, *args, **kwargs):
        # Check if entry already exists for this date
        date = request.data.get('date')
        existing_entry = JournalEntry.objects.filter(
            user=request.user,
            date=date
        ).first()
        
        if existing_entry:
            return Response(
                {"detail": "Entry already exists for this date. Use update instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JournalEntryRetrieveUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Allow lookup by date or pk
        date = self.request.query_params.get('date', None)
        if date:
            obj = get_object_or_404(
                JournalEntry,
                user=self.request.user,
                date=date
            )
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Handle partial updates (PATCH)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)