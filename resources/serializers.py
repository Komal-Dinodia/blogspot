from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework.exceptions import ValidationError
from resources.models import Blog
from django.utils.text import slugify  


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
class BlogSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length = 1000)  
    image = serializers.ImageField(required=False)  

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'description', 'tags', 'image', 'likes', 'views', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['slug'] 


    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        
        original_slug = validated_data['slug']
        count = 1
        while Blog.objects.filter(slug=validated_data['slug']).exists():
            validated_data['slug'] = f"{original_slug}-{count}"
            count += 1

        return super().create(validated_data)
