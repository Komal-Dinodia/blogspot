from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from resources.models import Blog, Comment
from resources.serializers import BlogGetSerializer, BlogDetailSeriazlizer, CommentSeriazlizer, \
    CommentGetSeriazlizer
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC


class CustomPagination(PageNumberPagination):
    page_size = 3


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
        queryset = Blog.objects.filter(is_published=True, user=request.user)

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
                email_confirmation = EmailConfirmationHMAC.from_key(key)
                if not email_confirmation:
                    email_confirmation = get_object_or_404(EmailConfirmation, key=key)
                
                email_confirmation.confirm(request)
                return Response("Email verified successfully!", status=status.HTTP_400_BAD_REQUEST)

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

        
