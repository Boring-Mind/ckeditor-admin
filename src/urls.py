from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from src.blog_admin import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('secret/', views.SecretView.as_view(), name='secret'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('posts/create/', views.PostFormView.as_view(), name='create_post'),
    path('tags/get/', views.TagsRetrieveView.as_view(), name='get_tags'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
