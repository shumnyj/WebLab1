from django.urls import path

from . import views

app_name = 'online_libr'
urlpatterns = [
    path(r'', views.index_view, name='index'),
    path('book/<int:book_id>', views.book_view, name='book'),
    path('profile/<int:user_id>', views.profile_view, name='profile'),
    path('profile/edit', views.profile_edit_view, name='profile_edit'),
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
]