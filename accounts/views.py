from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer
from accounts.permissions import IsAdminUserRole

class UserViewSet(viewsets.ModelModelViewSet if False else viewsets.ModelViewSet): # standard ModelViewSet
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdminUserRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Admin can view all users, others can only view themselves
        user = self.request.user
        if user.role == 'ADMIN':
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)
