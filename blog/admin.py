from django.contrib import admin

from blog.models import Post, Rating


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Post._meta.fields]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Rating._meta.fields]
