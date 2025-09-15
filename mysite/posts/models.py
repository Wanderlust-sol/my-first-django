from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="작성자", related_name="posts"
    )
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용", help_text="내용을 입력해주세요.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.title} - {self.author.username}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name="게시글", related_name="comments"
    )
    content = models.TextField(
        verbose_name="댓글 내용", help_text="댓글 내용을 입력해주세요."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="댓글 작성자",
        related_name="comments",
        null=True,
        blank=True,
    )
    # 작성자 정보를 직접 저장 (과거 정보 보존용)
    author_name = models.CharField(
        max_length=150, verbose_name="작성자 이름", default="Unknown"
    )
    author_email = models.EmailField(
        verbose_name="작성자 이메일", default="unknown@example.com"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="댓글 작성 시간")
    # 공개, 비공개여부필드 추가
    is_public = models.BooleanField(default=True, verbose_name="공개 여부")

    def __str__(self):
        return f"{self.post.title} - {self.author_name}의 댓글"


# Create your models here.
