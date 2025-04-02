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

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password1 = serializers.CharField(max_length=50)
    password2 = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ForgotConfirmPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=50)
    new_password2 = serializers.CharField(max_length=50)
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=50)
    new_password = serializers.CharField(max_length=50)

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
        return f'http://103.206.101.251:8003/media/{obj.image}'

        
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
            return f'http://103.206.101.251:8003/media/{obj.image}'
        else:
            return obj.image
        
    def get_author(self, obj):
        return f"{obj.user.username if obj.user.username else ''} {obj.user.last_name if obj.user.last_name else ''}"   


class CommentSeriazlizer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment']  


class CommentGetSeriazlizer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id','comment','user','created_at']
    
    def get_user(self, obj):
        return f"{obj.user.username if obj.user.username else ''}"   

class CreateBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['title', 'description','image']
    
    def validate_title(self, value):
        if not value.strip():  # Check if title is empty or contains only spaces
            raise serializers.ValidationError("Title field is required.")
        if len(value) < 2:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value

    def validate_description(self, value):
        if not value.strip():  # Check if description is empty or contains only spaces
            raise serializers.ValidationError("Description field is required.")
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value