from services.views import TagCreateView
from django.urls import path
from .views import VendorCreateView, VendorListView, VendorDeleteView, TagCreateView, TagDeleteView, TagListView, VendorRetrieveUpdateView

urlpatterns=[
    path('tag/create', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list', TagListView.as_view(), name = 'tag-list'),
    path('tag/delete/<str:name>/', TagDeleteView.as_view(), name = 'tag-delete'),
    path('vendor/create', VendorCreateView.as_view(), name = 'vendor-create'),
    path('vendor/delete/<str:id>/', VendorDeleteView.as_view(), name = 'vendor-delete'),
    path('vendor/retrieve/<str:id>/', VendorRetrieveUpdateView.as_view(), name = 'vendor-retrieve'),
    path('vendor/list/', VendorListView.as_view(), name = 'vendor-list')
]