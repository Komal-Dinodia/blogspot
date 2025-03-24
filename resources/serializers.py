from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework.exceptions import ValidationError
from resources.models import Blog, Comment
from django.utils.text import slugify  
from django.conf import settings


User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()

class CustomLoginSerializer(LoginSerializer):
    username = None  
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("Invalid email or password")

        email_verified = EmailAddress.objects.filter(email=email, verified=True).exists()
        if not email_verified:
            raise ValidationError("Email is not verified. Please check your inbox.")

        return super().validate(attrs)
    

class BlogGetSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'slug', 'title', 'image', 'likes', 'views', 'updated_at' ,'user', 'comment_count', 'author'
        ]    

    def get_comment_count(self, obj):
        return Comment.objects.filter(blog=obj).count()
    
    def get_image(self, obj):
        if settings.DEBUG:
            return f'http://127.0.0.1:8000/media/{obj.image}'
        else:
            return obj.image
        
    def get_author(self, obj):
        return f"{obj.user.first_name if obj.user.first_name else ''} {obj.user.last_name if obj.user.last_name else ''}"   
    
class BlogDetailSeriazlizer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'slug', 'title', 'image', 'likes', 'views', 'updated_at' ,'user', 'comment_count', 'author', 'description'
        ]    

    def get_comment_count(self, obj):
        return Comment.objects.filter(blog=obj).count()
    
    def get_image(self, obj):
        if settings.DEBUG:
            return f'http://127.0.0.1:8000/media/{obj.image}'
        else:
            return obj.image
        
    def get_author(self, obj):
        return f"{obj.user.first_name if obj.user.first_name else ''} {obj.user.last_name if obj.user.last_name else ''}"   
      