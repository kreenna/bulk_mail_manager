from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, UsersListView, ProfileDetailView, ProfileUpdateView, ProfileDeleteView, CustomPasswordChangeView, \
    activate

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/delete/<int:pk>/', ProfileDeleteView.as_view(), name='profile_delete'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('users/users_list/', UsersListView.as_view(), name='users_list'),
]
