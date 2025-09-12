from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from posts.models import Post, Comment


class PostModelTest(TestCase):
    """Post 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            author=self.user, title="테스트 게시글", content="테스트 내용입니다."
        )

    def test_post_creation(self):
        """게시글 생성 테스트"""
        self.assertEqual(self.post.title, "테스트 게시글")
        self.assertEqual(self.post.content, "테스트 내용입니다.")
        self.assertEqual(self.post.author, self.user)
        self.assertIsNotNone(self.post.created_at)
        self.assertIsNotNone(self.post.updated_at)

    def test_post_str_representation(self):
        """게시글 문자열 표현 테스트"""
        expected_str = f"{self.post.title} - {self.post.author.username}"
        self.assertEqual(str(self.post), expected_str)

    def test_post_verbose_names(self):
        """게시글 필드 verbose_name 테스트"""
        self.assertEqual(Post._meta.get_field("author").verbose_name, "작성자")
        self.assertEqual(Post._meta.get_field("title").verbose_name, "제목")
        self.assertEqual(Post._meta.get_field("content").verbose_name, "내용")
        self.assertEqual(Post._meta.get_field("created_at").verbose_name, "작성일")
        self.assertEqual(Post._meta.get_field("updated_at").verbose_name, "수정일")


class CommentModelTest(TestCase):
    """Comment 모델 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            author=self.user, title="테스트 게시글", content="테스트 내용입니다."
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content="테스트 댓글입니다."
        )

    def test_comment_creation(self):
        """댓글 생성 테스트"""
        self.assertEqual(self.comment.content, "테스트 댓글입니다.")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post, self.post)
        self.assertIsNotNone(self.comment.created_at)

    def test_comment_verbose_names(self):
        """댓글 필드 verbose_name 테스트"""
        self.assertEqual(Comment._meta.get_field("post").verbose_name, "게시글")
        self.assertEqual(Comment._meta.get_field("content").verbose_name, "댓글 내용")
        self.assertEqual(Comment._meta.get_field("author").verbose_name, "댓글 작성자")
        self.assertEqual(
            Comment._meta.get_field("created_at").verbose_name, "댓글 작성 시간"
        )

    def test_comment_post_relationship(self):
        """댓글과 게시글 관계 테스트"""
        self.assertEqual(self.comment.post, self.post)
        self.assertIn(self.comment, self.post.comment_set.all())


class PostListAPITest(APITestCase):
    """PostList API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post1 = Post.objects.create(
            author=self.user, title="첫 번째 게시글", content="첫 번째 내용입니다."
        )
        self.post2 = Post.objects.create(
            author=self.user, title="두 번째 게시글", content="두 번째 내용입니다."
        )

    def test_get_posts_list(self):
        """게시글 목록 조회 테스트"""
        url = reverse("post-list")  # URL 패턴에 따라 수정 필요
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # 첫 번째 게시글 검증
        first_post = response.data[0]
        self.assertEqual(first_post["title"], "첫 번째 게시글")
        self.assertEqual(first_post["content"], "첫 번째 내용입니다.")
        self.assertEqual(first_post["author"], self.user.id)
        self.assertIn("created_at", first_post)
        self.assertIn("updated_at", first_post)

    def test_get_posts_empty_list(self):
        """빈 게시글 목록 조회 테스트"""
        Post.objects.all().delete()
        url = reverse("post-list")  # URL 패턴에 따라 수정 필요
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class PostCommentRelationshipTest(TestCase):
    """게시글과 댓글 관계 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )
        self.post = Post.objects.create(
            author=self.user1, title="테스트 게시글", content="테스트 내용입니다."
        )

    def test_post_has_comments(self):
        """게시글에 댓글이 있는 경우 테스트"""
        comment1 = Comment.objects.create(
            post=self.post, author=self.user1, content="첫 번째 댓글"
        )
        comment2 = Comment.objects.create(
            post=self.post, author=self.user2, content="두 번째 댓글"
        )

        self.assertEqual(self.post.comment_set.count(), 2)
        self.assertIn(comment1, self.post.comment_set.all())
        self.assertIn(comment2, self.post.comment_set.all())

    def test_post_no_comments(self):
        """게시글에 댓글이 없는 경우 테스트"""
        self.assertEqual(self.post.comment_set.count(), 0)

    def test_comment_belongs_to_post(self):
        """댓글이 특정 게시글에 속하는지 테스트"""
        comment = Comment.objects.create(
            post=self.post, author=self.user1, content="테스트 댓글"
        )

        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.post.author, self.user1)
