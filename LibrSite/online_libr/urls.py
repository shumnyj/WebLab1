from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from . import views
from .views import ApiRouter
from .models import ChatUser

app_name = 'online_libr'

urlpatterns = [
    path(r'', views.index_view, name='index'),
    path('book/<int:book_id>', views.BookView.as_view(), name='book'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/reviews', views.UserReviewsView.as_view(), name='user_reviews'),
    path('profile/edit', views.ProfileUpdate.as_view(), name='profile_edit'),
    path('search', views.search_view, name='search'),
    path('browse', views.browse_view, name='browse'),
    path('about', views.about_view, name='about'),

    path('login', views.MyLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),

    path(r'api/', include((ApiRouter.urls, ''))),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='online_libr:schema'), name='redoc'),

    # path('chat/webhook/', views.chat_webhook),
    path('chat/online/', views.chat_users, name='chat_users'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/kick/<int:pk>',  views.kick_chat_user, name='kick_chat_user'),

    path('tasks/', views.tasks_view, name='tasks'),
]

ChatUser.objects.all().delete()
