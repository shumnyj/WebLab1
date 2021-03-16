from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('<int:book_id>', views.book_view, name='book'),
    path('profile/<int:user_id>', views.profile_view, name='profile'),
    path('profile/edit', views.profile_edit_view, name='profile_edit'),
]