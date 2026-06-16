from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from accounts.permissions import IsAdminUserRole, IsFacultyUserRole
from lms.models import LMSMaterial
from lms.serializers import LMSMaterialSerializer

class LMSMaterialViewSet(viewsets.ModelViewSet):
    queryset = LMSMaterial.objects.all().order_by('-uploaded_at')
    serializer_class = LMSMaterialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'subject__name', 'subject__code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsFacultyUserRole() | IsAdminUserRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Auto-set uploaded_by to current faculty user
        if hasattr(self.request.user, 'faculty_profile'):
            serializer.save(uploaded_by=self.request.user.faculty_profile)
        else:
            # Fallback for admin
            serializer.save()

    @action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        material = self.get_object()
        material.download_count += 1
        material.save()
        return Response({'status': 'success', 'download_count': material.download_count})
