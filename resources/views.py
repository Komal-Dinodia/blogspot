from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status, permissions,generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from resources.models import Blog, Comment, UserToken, CommentReply
from resources.serializers import BlogGetSerializer, BlogDetailSeriazlizer, CommentSeriazlizer, \
    CommentGetSeriazlizer, CreateBlogSerializer, SignupSerializer, LoginSerializer, \
    ForgotPasswordSerializer, ForgotConfirmPasswordSerializer, ChangePasswordSerializer, \
    CommentReplySerializer, CommentReplyGetSerializer
import smtplib
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class CustomPagination(PageNumberPagination):
    page_size = 3


class SignupView(APIView):
    def post(self,request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password1 = serializer.validated_data.get('password1')   
            password2 = serializer.validated_data.get('password2')
            first_name = serializer.validated_data.get('first_name')
            last_name = serializer.validated_data.get('last_name')

            username_exist = User.objects.filter(username=username).exists() #get username from User model and show error if already exist
            if username_exist == True:
                return Response({"A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            email_exist = User.objects.filter(email=email).exists() #get email from user model and show error if mail already exist
            if email_exist == True:
                return Response({"A user with that email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if password1!=password2:
                return Response({"Password doesn't match."},status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(username=username,email=email,first_name=first_name,last_name=last_name) #return all details in user
            user.set_password(password1)
            user.save()
            EmailAddress.objects.create(email=email,user=user,primary=True) #store email in emailaddress
            usertoken = UserToken.objects.create(user=user) #create token for verification
            usertoken.save()
            
            self.send_mail(email)
            return Response({"detail":"Verification e-mail sent."},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def send_mail(self,email):

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # message to be sent
        user_token = UserToken.objects.get(user__email=email)
        message = f"Hello,\n\n Please confirm your email here. \n http://103.206.101.251:5003/verify-email/{user_token.token}"
        # sending the mail
        s.sendmail(settings.EMAIL_HOST_USER, email, message)
        # terminating the session
        s.quit()

class LoginView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

        email_exist = User.objects.filter(email=email).exists()
        if email_exist!=True:
            return Response({"non_field_errors": ["Unable to log in with provided credentials."]},status=status.HTTP_400_BAD_REQUEST)
        
        email_verified = EmailAddress.objects.get(email=email).verified
        if email_verified==False:
            user = User.objects.get(email=email)
            token, created = UserToken.objects.get_or_create(user=user)  
            self.send_mail(email, token.token)
            return Response({"non_field_errors": ["Email not verified. Verification email sent again."]},status=status.HTTP_400_BAD_REQUEST,)
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            data = {}
            subdata = {}

            subdata["pk"] = user.id
            subdata["username"]= user.username
            subdata["email"] = user.email
            subdata["first_name"] = user.first_name
            subdata["last_name"] = user.last_name
            data["access"] = str(refresh.access_token)
            data["refresh"] = str(refresh)
            data["user"] = subdata
            return Response(data,status=status.HTTP_200_OK)
            
        else:
            return Response({"non_field_errors": ["Unable to log in with provided credentials."]},status=status.HTTP_400_BAD_REQUEST)
    def send_mail(self,email,token):

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # message to be sent
        user_token = UserToken.objects.get(user__email=email)
        message = f"Hello,\n\n Please confirm your email here. \n http://103.206.101.251:5003/verify-email/{user_token.token}"
        # sending the mail
        s.sendmail(settings.EMAIL_HOST_USER, email, message)
        # terminating the session
        s.quit()

class ResendEmailVerificationView(APIView):
    def post(self,request):
        data = request.data
        email = data.get('email')
        if not email:
            return Response({"error":["Please enter your email"]},status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                email_address = EmailAddress.objects.get(email=email)
                if email_address.verified:
                    return Response({"error":["user already verified"]},status=status.HTTP_400_BAD_REQUEST)
            
                user = User.objects.get(email=email)
                self.send_mail(email)
                return Response({"message": ["Verification email sent again."]},status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error":["User not found"]}, status=status.HTTP_404_NOT_FOUND)
            except EmailAddress.DoesNotExist:
                return Response({"error":["User not found"]}, status=status.HTTP_404_NOT_FOUND)
            
            
    def send_mail(self,email):

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # message to be sent
        user_token = UserToken.objects.get(user__email=email)
        message = f"Hello,\n\n Please confirm your email here. \n http://103.206.101.251:5003/verify-email/{user_token.token}"
        # sending the mail
        s.sendmail(settings.EMAIL_HOST_USER, email, message)
        # terminating the session
        s.quit()            

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            email_exist= User.objects.filter(email=email).exists()
            if email_exist == False:
                return Response({"details" :"This email is not registered"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                self.send_mail(email)
                return Response({"detail": "Password reset e-mail has been sent."},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def send_mail(self,email):

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # message to be sent
        user_token = UserToken.objects.get(user__email=email)
        message = f"Hello,\n\n Please reset your password here. \n http://103.206.101.251:5003/reset-password/{user_token.user.id}/{user_token.token}"
        # sending the mail
        s.sendmail(settings.EMAIL_HOST_USER, email, message)
        # terminating the session
        s.quit()

class ForgotConfirmPasswordView(APIView):
    def post(self, request):
        serializer = ForgotConfirmPasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password1 = serializer.validated_data.get('new_password1')
            new_password2 = serializer.validated_data.get('new_password2')
            uid = serializer.validated_data.get('uid')
            token = serializer.validated_data.get('token')
        
            if new_password1!=new_password2:
                return Response({"error":"Password doesn't match. "},status=status.HTTP_400_BAD_REQUEST)
            
            uid_exist = User.objects.filter(id=uid).exists()
            if uid_exist == False:
                return Response({"error":"User is not valid."},status=status.HTTP_400_BAD_REQUEST)
            token_exist = UserToken.objects.filter(token=token).exists()
            if token_exist == False:
                return Response({"error":"User is not valid."},status=status.HTTP_400_BAD_REQUEST)
            usertoken = UserToken.objects.get(token=token)
            user = usertoken.user
            user.set_password(new_password1)
            user.save()
            return Response({"details":"Password reset Successfully"},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            oldpassword = serializer.validated_data.get('old_password')
            newpassword = serializer.validated_data.get('new_password')
            if oldpassword==newpassword:
                return Response({"error":"Password can't be same. "},status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=request.user.username, password=oldpassword)
            if user is not None:    
                user.set_password(newpassword)
                user.save()
                return Response({"details":"Password changed successfully"},status=status.HTTP_200_OK)
            else:
                return Response({"error":"Old password is incorrect."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class LogoutView(APIView):
    def post(self,request):
        logout(request)
        return Response({"message":"user logout successfully"},status=status.HTTP_200_OK)


class BlogAPIView(APIView):

    def get(self, request):
        queryset = Blog.objects.filter(is_published=True)

        # Search filter: Filter posts by title
        search_query = request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = BlogGetSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class BlogDetailView(APIView):
    def get(self, request, slug):
        try:
            queryset = Blog.objects.get(slug=slug)
        except Exception as e:
            return Response("Blog not found", status=status.HTTP_404_NOT_FOUND)
        
        serializer = BlogDetailSeriazlizer(queryset)
        return Response(serializer.data)
    

class MyBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        queryset = Blog.objects.filter(user=request.user)

        # Search filter: Filter posts by title
        search_query = request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = BlogGetSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class VerifyEmailAPIVIew(APIView):

    def post(self, request):
        key = request.data.get('key')
        if key:
            try:
                user_token = UserToken.objects.get(token=key)
                email_address = EmailAddress.objects.get(user=user_token.user)
                email_address.verified=True
                email_address.save()
                return Response("Email verified successfully!", status=status.HTTP_200_OK)

            except Exception as e:
                return Response("Invalid or expired verification key.", status=status.HTTP_400_BAD_REQUEST)
        return Response("Invalid or expired verification key.", status=status.HTTP_400_BAD_REQUEST)

class ViewsCountApiView(APIView):
    
    def get(self, request, slug):
        blog = Blog.objects.get(slug=slug)
        blog.views += 1
        blog.save()
        return Response({})
    
class CommentCreateApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self,request, slug):
        user = request.user
        blog = Blog.objects.get(slug=slug)
        serializer = CommentSeriazlizer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, blog=blog)
            return Response("Comment added succesfully",status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CommentGetApiView(APIView):
    def get(self,request,slug):
        comment = Comment.objects.filter(blog__slug=slug)
        serializer = CommentGetSeriazlizer(comment,many=True)
        return Response(serializer.data)

        
class CreateBlogApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self,request):
        data = request.data
        serializer = CreateBlogSerializer(data=data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            slug = title.lower().replace(' ','-')
            serializer.save(user=request.user,slug=slug)
            return Response("Blog Created Successfuly",status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSeriazlizer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)

            # Only the comment owner can delete it
            if comment.user != request.user:
                return Response({"error": "You are not authorized to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        
class EditDeleteBlogAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, slug, user):
        """Retrieve the blog post and check permissions."""
        try:
            blog = Blog.objects.get(slug=slug)
            if blog.user != user:
                raise PermissionDenied("You do not have permission to edit or delete this blog.")
            return blog
        except Blog.DoesNotExist:
            return None

    def put(self, request, slug):
        """Handle blog editing."""
        blog = self.get_object(slug, request.user)
        if not blog:
            return Response({"error": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateBlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Blog updated successfully.", "blog": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        """Handle blog deletion."""
        blog = self.get_object(slug, request.user)
        if not blog:
            return Response({"error": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

        blog.delete()
        return Response({"message": "Blog deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class CommentReplyView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    seralizer = CommentReplySerializer

    def post(self,request, comment_id):
        data = request.data
        serializer = self.seralizer(data=data)
        if serializer.is_valid():
            comment = Comment.objects.get(id=comment_id)
            serializer.save(user=request.user, comment=comment)
            return Response({"message":"Reply added successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def get(self,request, comment_id):
        comment = CommentReply.objects.filter(comment__id=comment_id)
        serializer = CommentReplyGetSerializer(comment,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
