from celery import shared_task
from blog.models import Post


@shared_task()
def update_post_average_rating_task(post_id):
    try:
        Post.update_average_rating(post_id=post_id)
    except Exception as e:
        print(e)  # TODO: add log


@shared_task()
def add_posts_to_update_average_ratings():
    try:
        posts = Post.objects.filter(should_update_average_rating=True).only("id")
        for post in posts:
            update_post_average_rating_task.apply_async(
                kwargs={'post_id': post.id}, queue="blog_queue")
    except Exception as e:
        print(e)  # TODO: add log
