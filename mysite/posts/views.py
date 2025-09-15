# from django.shortcuts import render

from posts.models import Post
from posts.models import Comment

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class PostCreate(APIView):
    class PostSerializer(ModelSerializer):
        user_email = serializers.EmailField(write_only=True)

        class Meta:
            model = Post
            fields = [
                "user_email",
                "title",
                "content",
            ]

    def post(self, request):
        serializer = self.PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["user_email"])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                "author_name",
                "author_email",
                "created_at",
            ]

    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id)
        serializers = self.CommentSerializer(comments, many=True)

        return Response(serializers.data)


class CommentCreate(APIView):
    class CommentSerializer(ModelSerializer):
        user_email = serializers.EmailField(write_only=True)

        class Meta:
            model = Comment
            fields = [
                "user_email",
                "content",
            ]

        def validate_user_email(self, value):
            # 허용된 도메인 목록
            allowed_domains = ["salarify.kr", "naver.com", "gmail.com", "test.com"]
            domain = value.split("@")[-1]

            if domain not in allowed_domains:
                raise serializers.ValidationError(
                    f"허용되지 않은 이메일 도메인입니다. 허용된 도메인: {', '.join(allowed_domains)}"
                )
            return value

        def create(self, validated_data):
            # user_email을 제거하고 author를 설정
            user_email = validated_data.pop("user_email")
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "해당 이메일의 사용자를 찾을 수 없습니다."
                )
            except Exception as e:
                raise serializers.ValidationError("사용자 조회 중 오류가 발생했습니다.")

            # 작성자 정보를 직접 저장 (과거 정보 보존)
            validated_data["author"] = user
            validated_data["author_name"] = user.username
            validated_data["author_email"] = user.email
            return Comment.objects.create(**validated_data)

    def post(self, request, post_id):
        # post_id로 Post 객체 존재 확인
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "해당 게시글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # post_id를 validated_data에 추가
        request.data["post"] = post_id

        serializer = self.CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class PostDetail(APIView):
    class PostDetailSerializer(ModelSerializer):
        class CommentSerializer(ModelSerializer):
            class Meta:
                model = Comment
                fields = [
                    "id",
                    "content",
                    "author_name",
                    "author_email",
                    "created_at",
                ]

        comments = CommentSerializer(many=True)

        class Meta:
            model = Post
            fields = [
                "title",
                "content",
                "created_at",
                "comments",
            ]

    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        serializer = self.PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 유저별로 포스트와 댓글을 조회하는 APIView
class UserPostList(APIView):
    class UserPostListSerializer(ModelSerializer):
        class CommentSerializer(ModelSerializer):
            class Meta:
                model = Comment
                fields = [
                    "id",
                    "content",
                    "author_name",
                    "author_email",
                    "created_at",
                ]

        comments = CommentSerializer(many=True, read_only=True)

        class Meta:
            model = Post
            fields = [
                "id",
                "title",
                "content",
                "created_at",
                "author",
                "comments",
            ]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "해당 사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        posts = Post.objects.filter(author=user)
        serializer = self.UserPostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
