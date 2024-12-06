from django.urls import path
from blog.views import PostListView, RatingCreateUpdateView

urlpatterns = [
    path('posts/', PostListView.as_view()),
    path('posts/ratings', RatingCreateUpdateView.as_view()),
]
