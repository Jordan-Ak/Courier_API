from services.views import TagCreateView
from django.urls import path
from .views import VendorCreateView, VendorListView, VendorDeleteView, TagCreateView, TagDeleteView, TagListView

urlpatterns=[
    path('tag/create', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list', TagListView.as_view(), name = 'tag-list'),
    path('tag/delete/<str:name>/', TagDeleteView.as_view(), name = 'tag-delete'),
    path('vendor/create', VendorCreateView.as_view(), name = 'vendor-create'),
    path('vendor/delete/<str:name>/', VendorDeleteView.as_view(), name = 'vendor-delete'),
    path('vendor/list/', VendorListView.as_view(), name = 'vendor-list')
]