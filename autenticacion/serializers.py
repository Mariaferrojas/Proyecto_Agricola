from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate_username(self, value):
        """Validar que el username sea único y tenga caracteres válidos."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe.")
        if len(value) < 3:
            raise serializers.ValidationError("El username debe tener al menos 3 caracteres.")
        return value

    def validate_email(self, value):
        """Validar que el email sea único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate(self, attrs):
        """Validar que las contraseñas coincidan."""
        password = attrs.get('password')
        password2 = attrs.get('password2')
        
        if password != password2:
            raise serializers.ValidationError({
                'password': "Las contraseñas no coinciden.",
                'password2': "Las contraseñas no coinciden."
            })
        
        # Validar que la contraseña no sea muy simple
        if password.isdigit():
            raise serializers.ValidationError({
                'password': "La contraseña no puede ser solo números."
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        
        # Crear usuario
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
