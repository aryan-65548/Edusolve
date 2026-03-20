from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model
    
    Just like Hitesh teaches - we use ModelSerializer for automatic
    field generation from our model
    """
    
    class Meta:
        model = Student
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'grade',
            'phone_number',
            'profile_picture',
            'bio',
            'points',
            'preferred_subjects',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'points', 'created_at', 'updated_at']


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    
    Includes password confirmation and validation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )
    
    class Meta:
        model = Student
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'grade',
            'phone_number',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'grade': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Custom validation - Hitesh shows this technique!
        Check if passwords match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Override create method to handle password hashing
        """
        # Remove password2 as it's not a model field
        validated_data.pop('password2')
        
        # Create user with hashed password
        user = Student.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            grade=validated_data['grade'],
            phone_number=validated_data.get('phone_number', ''),
        )
        
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating student profile
    """
    class Meta:
        model = Student
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'grade',
            'phone_number',
            'profile_picture',
            'bio',
            'points',
            'preferred_subjects',
            'created_at',
        ]
        read_only_fields = ['id', 'username', 'points', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Check if new passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs