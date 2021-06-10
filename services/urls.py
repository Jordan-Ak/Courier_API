from services.views import TagCreateView
from django.urls import path
from .views import ServiceCreateView, ServiceDeleteView, ServiceListView, TagCreateView, TagDeleteView, TagListView

urlpatterns=[
    path('tag/create', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list', TagListView.as_view(), name = 'tag-list'),
    path('tag/delete/<str:name>/', TagDeleteView.as_view(), name = 'tag-delete'),
    path('vendor/create', ServiceCreateView.as_view(), name = 'service-create'),
    path('vendor/delete/<str:name>/', ServiceDeleteView.as_view(), name = 'service-delete'),
    path('vendor/list/', ServiceListView.as_view(), name = 'service-list')
]