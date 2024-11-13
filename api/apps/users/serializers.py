from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False},
            'role': {'required': False}
        }

    def create(self, validated_data):
        # Establecer is_authenticated basado en si hay contraseña
        is_authenticated = 'password' in validated_data and validated_data['password']
        
        # Manejar la contraseña si existe
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
        
        user.is_authenticated = is_authenticated
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        user = CustomUser.objects.filter(username=username).first()
        
        if not user:
            raise serializers.ValidationError({"detail": "Usuario no encontrado"})
            
        # Si el usuario ya está autenticado (tiene credenciales)
        if user.is_authenticated:
            # Usar la validación normal de JWT que incluye verificación de contraseña
            return super().validate(attrs)
        
        # Si el usuario no está autenticado (sin credenciales)
        self.user = user
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'needs_setup': True,
            'message': 'Se requiere configurar email y contraseña'
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['has_password'] = bool(user.password)
        token['has_email'] = bool(user.email)
        token['is_authenticated'] = user.is_authenticated
        return token

class SetupCredentialsSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        user = CustomUser.objects.filter(username=username).first()

        if not user:
            raise serializers.ValidationError({"detail": "Usuario no encontrado"})

        if user.is_authenticated:
            raise serializers.ValidationError({"detail": "Este usuario ya está autenticado"})

        return attrs

    def update(self, user, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')

        user.email = email
        user.set_password(password)
        user.is_authenticated = True
        user.save()

        # Generar nuevo token con privilegios completos
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
