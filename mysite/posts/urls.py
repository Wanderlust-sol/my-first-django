from django.urls import path
from posts import views

urlpatterns = [
    path("list/", views.PostList.as_view(), name="post-list"),
    path("<int:post_id>/comments/", views.CommentList.as_view()),
    path("<int:post_id>/comments/create/", views.CommentCreate.as_view()),
    path("create/", views.PostCreate.as_view()),
    path("detail/<int:pk>/", views.PostDetail.as_view()),
]
