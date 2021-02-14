from django.urls import path
from .views import posts_comment_and_list_view, like_dislike_post, PostDelete, PostUpdate

app_name = "posts"
urlpatterns = [
    path("", posts_comment_and_list_view, name="post"),
    path("like/", like_dislike_post, name="like"),
    path("<pk>/delete", PostDelete.as_view(), name="post-delete"),
    path("<pk>/update", PostUpdate.as_view(), name="post-update")
]
