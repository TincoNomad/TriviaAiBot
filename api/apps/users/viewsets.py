from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer
from api.utils.jwt_utils import IsAdminUser
from api.utils.logging_utils import log_exception, logger

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @log_exception
    def get_queryset(self):
        logger.debug(f"Retrieving users for admin: {self.request.user.username}")
        return CustomUser.objects.filter(created_by=self.request.user)
    
    @log_exception
    def perform_create(self, serializer):
        try:
            user = serializer.save(created_by=self.request.user)
            logger.info(f"New user created by admin {self.request.user.username}: {user.username}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @log_exception
    def perform_update(self, serializer):
        try:
            user = serializer.save()
            logger.info(f"User updated by admin {self.request.user.username}: {user.username}")
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    @log_exception
    def perform_destroy(self, instance):
        try:
            username = instance.username
            instance.delete()
            logger.info(f"User deleted by admin {self.request.user.username}: {username}")
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
