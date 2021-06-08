from services.views import TagCreateView
from django.urls import path
from .views import TagCreateView, TagListView

urlpatterns=[
    path('tag/create', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list', TagListView.as_view(), name = 'tag-list'),
]