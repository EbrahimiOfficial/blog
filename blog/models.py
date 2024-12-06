from django.db import models
from django.db import transaction as django_transaction
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import F, Avg, Prefetch

from model_utils.models import TimeStampedModel

from utils.exceptions import BadRequestException


class Post(TimeStampedModel):  # I usually use TimeStampedModel because it handles created and modified
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    should_update_average_rating = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['should_update_average_rating',]),
        ]

    def __str__(self):
        return self.title

    def create_or_update_rating(self, user, score):
        if not 1 <= score <= 5:
            raise BadRequestException("score should be greater than or equal to 1 and lower than or equal to 5")
        with django_transaction.atomic():
            rating, is_created = Rating.objects.get_or_create(post=self, user=user, defaults={"score": score})
            if is_created:
                self.should_update_average_rating = True
                self.rating_count = F("rating_count") + 1
                self.save(update_fields=["should_update_average_rating", "rating_count"])
            else:
                if rating.score != score:
                    rating.score = score
                    rating.save(update_fields=["score"])
                    self.should_update_average_rating = True
                    self.save(update_fields=["should_update_average_rating"])
        return rating

    @staticmethod
    def update_average_rating(post_id):
        with django_transaction.atomic():
            post = Post.objects.filter(id=post_id).select_for_update().get()
            if post.should_update_average_rating is False:
                return
            average_rating = Rating.objects.filter(post=post).aggregate(average_rating=Avg('score'))['average_rating']

            if average_rating is not None:
                post.average_rating = average_rating
            else:
                post.average_rating = 0  # set to 0 if there are no ratings

            post.should_update_average_rating = False
            post.save()

    @staticmethod
    def get_posts_and_user_ratings_v1(user):
        posts_data = cache.get('posts_data')
        if not posts_data:
            posts = Post.objects.all().only('id', 'title', 'average_rating', 'rating_count')
            posts_data = list(posts)
            cache.set('posts_data', posts_data, timeout=60)
        serialized_posts = []
        if user:
            user_ratings = Rating.objects.filter(
                post_id__in=[post.id for post in posts_data], user=user).values('post_id', 'score')
            user_ratings_dict = {ur['post_id']: ur['score'] for ur in user_ratings}
            for post in posts_data:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'average_rating': str(post.average_rating),
                    'rating_count': post.rating_count,
                    'user_rating': user_ratings_dict.get(post.id),
                }
                serialized_posts.append(post_data)
        else:
            for post in posts_data:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'average_rating': str(post.average_rating),
                    'rating_count': post.rating_count,
                    'user_rating': None,
                }
                serialized_posts.append(post_data)

        return serialized_posts

    @staticmethod
    def get_posts_and_user_ratings_v2(user):
        if user:
            posts = Post.objects.all().only('id', 'title', 'average_rating', 'rating_count').prefetch_related(
                Prefetch(
                    'ratings',
                    queryset=Rating.objects.filter(user=user),
                    to_attr='user_ratings'
                )
            )
            serialized_data = []
            for post in posts:
                user_rating = post.user_ratings[0].score if post.user_ratings else None
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'average_rating': str(post.average_rating),
                    'rating_count': post.rating_count,
                    'user_rating': user_rating,
                }
                serialized_data.append(post_data)
            return serialized_data
        else:
            serialized_data = cache.get('posts_data')
            if serialized_data:
                return serialized_data
            else:
                posts = Post.objects.all().only('id', 'title', 'average_rating', 'rating_count')
                serialized_data = [
                    {
                        'id': post.id,
                        'title': post.title,
                        'average_rating': str(post.average_rating),
                        'rating_count': post.rating_count,
                        'user_rating': None,
                    }
                    for post in posts
                ]
                cache.set('posts_data', serialized_data, timeout=60)
                return serialized_data


class Rating(TimeStampedModel):  # I usually use TimeStampedModel because it handles created and modified
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='ratings')
    score = models.SmallIntegerField(default=0)  # 0 to 5

    class Meta:
        unique_together = [["post", "user"]]
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

