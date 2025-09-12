# from django.shortcuts import render

from posts.models import Post
from posts.models import Comment

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User


class PostCreate(APIView):
    class PostSerializer(ModelSerializer):
        class Meta:
            model = Post
            fields = [
                "title",
                "content",
            ]

    def post(self, request):
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.first()  # 임시 기능
        Post.objects.create(
            author=user,
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
        )
        return Response(status=status.HTTP_201_CREATED)


class PostList(APIView):
    class PostSerializer(ModelSerializer):
        class Meta:
            model = Post
            fields = [
                "id",
                "author",
                "title",
                "content",
                "created_at",
                "updated_at",
            ]

    def get(self, request):
        posts = Post.objects.all()
        serializers = self.PostSerializer(posts, many=True)
        return Response(serializers.data)


class CommentList(APIView):
    class CommentSerializer(ModelSerializer):
        class Meta:
            model = Comment
            fields = [
                "id",
                "content",
                "author",
                "created_at",
            ]

    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id)
        serializers = self.CommentSerializer(comments, many=True)
        return Response(serializers.data)
