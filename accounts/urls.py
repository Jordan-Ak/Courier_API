from django.urls import path
from accounts.views import UserCreateView, UserDeleteView, UserRetrieveView, UserUpdateView


urlpatterns = [
    path('signup/', UserCreateView.as_view(), name = 'signup'),
    path('me/', UserRetrieveView.as_view(), name ='user-retrieve'),
    path('me/update/', UserUpdateView.as_view(), name= 'user-update'),
    path('delete/<str:email>/', UserDeleteView.as_view(), name = 'user-delete'),
]