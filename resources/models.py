from django.contrib.auth.models import User
import uuid
from django.db import models
from ckeditor.fields import RichTextField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class UserToken(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4,unique=True)

class Blog(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=150, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = RichTextField()
    tags = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to='post_image/',blank=True, null=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.blog.title}"

