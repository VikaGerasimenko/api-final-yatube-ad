from rest_framework import serializers
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'text', 'author', 'image', 'group', 'pub_date')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    following = serializers.StringRelatedField(read_only=True)
    following_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following', 'following_id')
        read_only_fields = ('user',)

    def validate_following_id(self, value):
        request_user = self.context['request'].user
        if request_user.id == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'Пользователь не найден')
        if Follow.objects.filter(
            user=request_user,
            following_id=value
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        following_id = validated_data['following_id']
        following = User.objects.get(id=following_id)
        return Follow.objects.create(user=user, following=following)
