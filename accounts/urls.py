from django.urls import path
from accounts.views import UserAdminDetailView, UserAdminListView, UserCreateView, UserDeleteView, UserRetrieveView, UserUpdateView


urlpatterns = [
    path('signup/', UserCreateView.as_view(), name = 'signup'),
    path('me/', UserRetrieveView.as_view(), name ='user-retrieve'),
    path('me/update/', UserUpdateView.as_view(), name= 'user-update'),
    path('delete/<str:email>/', UserDeleteView.as_view(), name = 'user-delete'),
    path('list/', UserAdminListView.as_view(), name = 'user-list'),
    path('detail/<str:id>/', UserAdminDetailView.as_view(), name = 'user-detail'),
]