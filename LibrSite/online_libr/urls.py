from django.urls import path

from . import views

app_name = 'online_libr'
urlpatterns = [
    path(r'', views.index_view, name='index'),
    path('book/<int:book_id>', views.BookView.as_view(), name='book'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path('profile/edit', views.profile_edit_view, name='profile_edit'),
    path('browse', views.browse_view, name='browse'),
    path('about', views.about_view, name='about'),

    path('login', views.MyLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
]