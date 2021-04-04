from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.schemas import get_schema_view as gsv
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from . import views
from .views import ApiRouter

"""schema_view = get_schema_view(
    openapi.Info(
      title="Online Library API",
      default_version='v1',
      description="Redoc api for online library app",
      contact=openapi.Contact(email="troian.tbv@gmail.com"),
      license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)"""


app_name = 'online_libr'

urlpatterns = [
    path(r'', views.index_view, name='index'),
    path('book/<int:book_id>', views.BookView.as_view(), name='book'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path('profile/edit', views.ProfileUpdate.as_view(), name='profile_edit'),
    path('browse', views.browse_view, name='browse'),
    path('about', views.about_view, name='about'),

    path('login', views.MyLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),

    path('api/', include(ApiRouter.urls)),

    # path(r'api/schema/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path(r'api/schema/', schema_view.without_ui(cache_timeout=0), name='schema'),   # debug

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='online_libr:schema'), name='redoc'),

]
"""path(r'api/openapi/', gsv(
        title="Your Project",
        description="API for all things …",
        version="1.0.0",
        patterns=ApiRouter.urls,
        urlconf='online_libr.urls'

    ), name='openapi-schema'),"""