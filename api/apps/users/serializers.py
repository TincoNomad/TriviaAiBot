from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLES, default='user')

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'role', 'is_verified', 'created_by')
        read_only_fields = ('is_verified', 'created_by')

    def create(self, validated_data):
        request = self.context.get('request')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user'),
            created_by=request.user if request and request.user.is_authenticated else None
        )
        return user
