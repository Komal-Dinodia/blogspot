from django.contrib import admin
from django.urls import path, include
from resources.views import blog_posts, blog_post_detail  


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/posts/', blog_posts, name='blog_posts'),  
    path('api/posts/<int:pk>/', blog_post_detail, name='blog_post_detail'),  

]
