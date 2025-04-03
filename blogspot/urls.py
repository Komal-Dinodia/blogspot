from django.contrib import admin
from django.urls import path, include
from resources.views import BlogAPIView, BlogDetailView, MyBlogAPIView, VerifyEmailAPIVIew, \
    ViewsCountApiView, CommentCreateApiView, CommentGetApiView,CreateBlogApiView, \
    EditDeleteBlogAPIView, DeleteCommentView, SignupView, LoginView, ForgotPasswordView, \
    ForgotConfirmPasswordView, ChangePasswordView, ResendEmailVerificationView, \
    CommentReplyView, LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Below are the custom urls
    path('auth/registration/', SignupView.as_view()),
    path('auth/registration/verify/email/', VerifyEmailAPIVIew.as_view()),
    path('auth/login/',LoginView.as_view()),
    path('auth/logout/',LogoutView.as_view()),
    path('auth/password/reset/',ForgotPasswordView.as_view()),
    path('auth/password/reset/confirm/',ForgotConfirmPasswordView.as_view()),
    path('auth/resend/verify-email/',ResendEmailVerificationView.as_view()),
    path('auth/change/password/',ChangePasswordView.as_view()),
    path('api/blog/', BlogAPIView.as_view()), 
    path('api/blog/<slug:slug>/', BlogDetailView.as_view()),
    path('api/my/blog/', MyBlogAPIView.as_view()),
    path('api/blog/views/<slug:slug>/', ViewsCountApiView.as_view()),
    path('api/blog/create/comment/<slug:slug>/',CommentCreateApiView.as_view()),
    path('api/blog/get/comment/<slug:slug>/',CommentGetApiView.as_view()), 
    path("api/blog/delete/comment/<int:comment_id>/", DeleteCommentView.as_view(), name="delete-comment"),
    path('api/create/blog/',CreateBlogApiView.as_view()),
    path('blog/edit-delete/<slug:slug>/', EditDeleteBlogAPIView.as_view(), name='edit-delete-blog'),
    path('api/comment/reply/<int:comment_id>/',CommentReplyView.as_view()),


]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
