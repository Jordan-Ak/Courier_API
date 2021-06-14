from services.views import TagCreateView
from django.urls import path
from .views import (ScheduleCreateView, ScheduleDeleteView, ScheduleListView, ScheduleRetrieveListView, ScheduleRetrieveUpdateView, VendorCreateView, 
                    VendorListView, VendorDeleteView, 
                    TagCreateView, TagDeleteView, 
                    TagListView, VendorRetrieveUpdateView,)

urlpatterns=[
    path('tag/create', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list', TagListView.as_view(), name = 'tag-list'),
    path('tag/delete/<str:name>/', TagDeleteView.as_view(), name = 'tag-delete'),
    path('vendor/create', VendorCreateView.as_view(), name = 'vendor-create'),
    path('vendor/delete/<str:id>/', VendorDeleteView.as_view(), name = 'vendor-delete'),
    path('vendor/retrieve/<str:id>/', VendorRetrieveUpdateView.as_view(), name = 'vendor-retrieve'),
    path('vendor/list/', VendorListView.as_view(), name = 'vendor-list'),
    path('schedule/create/<str:vendor>/',ScheduleCreateView.as_view(), name = 'schedule-create'),
    path('schedule/list/', ScheduleListView.as_view(), name = 'schedule-list'),
    path('schedule/list/<str:vendor>/', ScheduleRetrieveListView.as_view(), name = 'schedule-vendor-retrieve'),
    path('schedule/<str:vendor>/<int:weekday>/', ScheduleRetrieveUpdateView.as_view(),
                                                                 name = 'schedule-weekday'),
    path('schedule/delete/<str:vendor>/', ScheduleDeleteView.as_view(), name='schedule-delete'),
]