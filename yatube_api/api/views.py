from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Post, Group
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    PostSerializer,
    CommentSerializer,
    GroupSerializer,
    FollowSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet. Для получения список всех постов или создания нового поста.
    Для получения, редактирования или удаления поста по 'id'.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet. Для получения  списка всех групп.
    Для получения информации о группе по 'id'.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet. Для получения списка всех комментариев поста с 'id=post_id'
    или создания нового комментария.
    Для получения, редактирования или удаляем комментария по 'id'
    у поста с 'id=post_id'.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsAuthorOrReadOnly]

    def get_post(self):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, id=post_id)

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            post=self.get_post(),
            author=self.request.user
        )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet. Для получения  списка всех групп.
    Для получения информации о группе по 'id'.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ListCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """Набор mixins для FollowViewSet"""
    pass


class FollowViewSet(ListCreateViewSet):
    """
    ViewSet. Для получения  списка всех подписок.
    Для подписки на авторов.
    """
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username',)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.request.user.follower.all()
