from django.contrib import admin
from django.urls import path, include
from resources.views import BlogAPIView, BlogDetailView, MyBlogAPIView, VerifyEmailAPIVIew
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/registration/verify/email/', VerifyEmailAPIVIew.as_view()),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/blog/', BlogAPIView.as_view()), 
    path('api/blog/<slug:slug>/', BlogDetailView.as_view()),
    path('api/my/blog/', MyBlogAPIView.as_view()),  

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
