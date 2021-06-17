from services.views import TagCreateView
from django.urls import path
from .views import (ProductCategoryCreateView, ProductCategoryDeleteView,
                    ProductCategoryListView, ProductCategoryRetrieveUpdateView,
                    ProductCreateView, ProductDeleteView, ProductListView,
                    ProductRetrieveUpdateView, ProductVendorListView, 
                    ScheduleCreateView, ScheduleDeleteView, ScheduleListView,
                    ScheduleRetrieveListView, ScheduleRetrieveUpdateView, VendorCreateView, 
                    VendorListView, VendorDeleteView, 
                    TagCreateView, TagDeleteView, 
                    TagListView, VendorRetrieveUpdateView,)

urlpatterns=[
    #Url for tag creation
    path('tag/create/', TagCreateView.as_view(), name = 'tag-create'),
    path('tag/list/', TagListView.as_view(), name = 'tag-list'),
    path('tag/delete/<str:name>/', TagDeleteView.as_view(), name = 'tag-delete'),
    
    #Urls for Vendors
    path('vendor/create/', VendorCreateView.as_view(), name = 'vendor-create'),
    path('vendor/delete/<str:id>/', VendorDeleteView.as_view(), name = 'vendor-delete'),
    path('vendor/retrieve/<str:id>/', VendorRetrieveUpdateView.as_view(), name = 'vendor-retrieve'),
    path('vendor/list/', VendorListView.as_view(), name = 'vendor-list'),
    
    #Urls for Schedules
    path('schedule/create/<str:vendor>/',ScheduleCreateView.as_view(), name = 'schedule-create'),
    path('schedule/list/', ScheduleListView.as_view(), name = 'schedule-list'),
    path('schedule/list/<str:vendor>/', ScheduleRetrieveListView.as_view(),
                                         name = 'schedule-vendor-retrieve'),
    path('schedule/<str:vendor>/<int:weekday>/', ScheduleRetrieveUpdateView.as_view(),
                                                                 name = 'schedule-weekday'),
    path('schedule/delete/<str:vendor>/', ScheduleDeleteView.as_view(), name='schedule-delete'),
    
    #Urls for product category
    path('product_cat/create/<str:vendor>/', ProductCategoryCreateView.as_view(),
                                                         name = 'product-cat-create'),
    path('product_cat/list/<str:vendor>/', ProductCategoryListView.as_view(),
                                                     name = 'product-cat-list'),
    path('product_cat/retrieve/<str:vendor>/<slug:slug_name>/', ProductCategoryRetrieveUpdateView.as_view(),
                                                            name = 'product-cat-update'),
    path('product_cat/delete/<str:vendor>/<slug:slug_name>/', ProductCategoryDeleteView.as_view(),
                                                            name ='product-cat-delete',),
    path('product/create/<str:vendor>/', ProductCreateView.as_view(), name = 'product-create'),
    path('product/list', ProductListView.as_view(), name = 'product-list'),
    path('product/list/<str:vendor>/', ProductVendorListView.as_view(), name = 'product-vendor-list'),
    path('product/retrieve/<str:vendor>/<str:product_cat>/<slug:slug_name>/',
                                        ProductRetrieveUpdateView.as_view(), name = 'product-retrieve'),
    path('product/delete/<str:vendor>/<str:product_cat>/<slug:slug_name>/',
                                        ProductDeleteView.as_view(), name = 'product-delete'),                                    
]