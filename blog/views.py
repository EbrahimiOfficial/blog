from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post
from utils.exceptions import BadRequestException


class PostListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user if request.user.is_authenticated else None
            # response = Post.get_posts_and_user_ratings_v1(user=user)
            response = Post.get_posts_and_user_ratings_v2(user=user)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e) # TODO: add log
            return Response({"Error": "Internal Server Error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RatingCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request_body = request.data

            if request_body.get("post_id") is None or request_body.get("score") is None:
                return Response({"detail": "post_id and score is required."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                post = Post.objects.get(id=request_body["post_id"])
            except Post.DoesNotExist:
                return Response({"detail": "post with given post_id does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)
            rating = post.create_or_update_rating(user=request.user, score=request_body["score"])
            return Response({"success": True}, status=status.HTTP_200_OK)
        except BadRequestException as bre:
            return Response({"detail": str(bre)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e) # TODO: add log
            return Response({"Error": "Internal Server Error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
