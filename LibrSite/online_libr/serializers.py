from rest_framework import serializers,  permissions, validators

from django.contrib.auth.models import User
from . import models as olm


class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return permissions.IsAdminUser.has_permission(self, request, view)


class UserSerializer(serializers.ModelSerializer):
    # libuser = serializers.PrimaryKeyRelatedField(many=False, queryset=olm.LibUser.objects.all())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'libuser']  #
        depth = 1


class BookSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="online_libr:book-detail")
    reviews = serializers.HyperlinkedIdentityField(view_name='online_libr:book-reviews', read_only=True)

    class Meta:
        model = olm.Book
        fields = ['url', 'id', 'title', 'author', 'publisher', 'pub_date', 'reviews']


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="online_libr:review-detail")
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.HyperlinkedRelatedField(view_name="online_libr:user-detail", read_only=True)
    book = serializers.HyperlinkedRelatedField(view_name="online_libr:book-detail", read_only=True)

    class Meta:
        model = olm.Review
        fields = ['url', 'id', 'user', 'book', 'rating', 'comment']  #


class ReviewSerializerPost(ReviewSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=olm.Book.objects.all())


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="online_libr:readstatus-detail")
    user = serializers.HyperlinkedRelatedField(view_name="online_libr:user-detail", read_only=True)  # default=serializers.CurrentUserDefault()
    book = serializers.HyperlinkedRelatedField(view_name="online_libr:book-detail", read_only=True)

    class Meta:
        model = olm.ReadStatus
        fields = ['url', 'id', 'user', 'book', 'status', 'date']  #


class StatusSerializerPost(StatusSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=olm.Book.objects.all())