from services.services import (customer_cart_get, customer_order_create, product_category_create, product_category_delete,
                               product_category_update, product_category_ven_cat_filter, 
                               product_category_ven_filter, product_create, product_delete, product_update, 
                               product_user_validation, product_ven_pro_cat_slug_filter,
                               rating_create, rating_delete, rating_get_id,
                               rating_update, rating_user_validation, schedule_create, 
                               schedule_update, schedule_vendor_day_filter, 
                               schedule_vendor_filter, vendor_create, vendor_delete, 
                               vendor_get_id, vendor_get_name, tag_create, 
                               tag_delete, vendor_get_user, vendor_retrieve_validation, vendor_update)

from services.serializers import (CustomerCartRetrieveUpdateSerializer, CustomerOrderCreateSerializer,
                                  ProductCategoryCreateSerializer, ProductCategoryListSerializer,
                                  ProductCategoryRetrieveUpdateSerializer,
                                  ProductCreateSerializer, ProductListSerializer,
                                  ProductRetrieveUpdateSerializer, ProductVendorListSerializer,
                                  RatingCreateSerializer, RatingListSerializer,
                                  RatingListUserSerializer, RatingRetrieveSerializer,
                                  RatingUpdateSerializer,
                                  ScheduleCreateSerializer,ScheduleListSerializer, 
                                  ScheduleRetrieveListSerializer,
                                  ScheduleRetrieveUpdateSerializer,
                                  VendorCreateSerializer, 
                                  VendorListSerializer,
                                  TagCreateSerializer, 
                                  TagListSerializer, 
                                  VendorRetrieveSerializer,
                                  VendorUpdateSerializer)

from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.views import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Product, ProductCategory, Rating, Schedule, Vendor, Tag
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwner

class TagCreateView(APIView):
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser] #Only Admins can create Tags

    @swagger_auto_schema(operation_id='Create a Tag', operation_description='Tag Creation endpoint',
                         request_body=TagCreateSerializer,
                         responses={'200': 'Tag created Successfully'})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception= True)
        data = serializer.validated_data
        tag_create(data['name'])
        return Response({'message':'Tag created Succesfully'}, status = status.HTTP_201_CREATED)

class TagListView(generics.ListAPIView):
    serializer_class = TagListSerializer
    permission_classes = [permissions.IsAdminUser] #Only admins have access to all tags at once at this endpoint.
    queryset = Tag.objects.all()

class TagDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser] #Only admin users can delete tags.

    @swagger_auto_schema(operation_id='Delete Tag', operation_description='Tag delete endpoint',
                         request_body=None,
                         responses={'200': 'Tag deleted Successfully'})
    def post(self, request, *args, **kwargs):
        tag_select = kwargs['name'] #getting specific tag from url using tag name
        tag = get_object_or_404(Tag.objects.all(), name = tag_select)
        tag_delete(tag)
        return Response({'message':'Tag deleted successfully'}, status=status.HTTP_200_OK)


class VendorCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated] #Have to be authenticated to create a vendor
    serializer_class = VendorCreateSerializer           #Vendor are associated with a user.

    @swagger_auto_schema(operation_id='Create a New Vendor', operation_description='Vendor create endpoint',
                         request_body=VendorCreateSerializer,
                         responses={'200': VendorCreateSerializer()})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user
        vendor_create(user,**data)
        return Response({'message':'New Vendor has been created Successfully'},
                                                 status= status.HTTP_201_CREATED)

class VendorRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class_GET = VendorRetrieveSerializer
    serializer_class_PUT = VendorUpdateSerializer

    @swagger_auto_schema(operation_id='Retrieve specific vendor',
                          operation_description='Vendor retreive endpoint',
                         request_body=None,
                         responses={'200': VendorRetrieveSerializer()})
    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        user_id = self.request.user.id
        vendor_retrieve_validation(vendor, user_id)
        serializer = self.serializer_class_GET(vendor)
        return Response(serializer.data)

    @swagger_auto_schema(operation_id='Update vendor', operation_description='Vendor update endpoint',
                         request_body=VendorUpdateSerializer,
                         responses={'200': VendorUpdateSerializer()})
    def put(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        user_id = self.request.user.id
        vendor_retrieve_validation(vendor, user_id)
        serializer = self.serializer_class_PUT(data = request.data,)# instance = vendor)
        serializer.is_valid(raise_exception=True)
        vendor_update(vendor,**serializer.validated_data)
        
        return Response({'message':'Vendor details Successfully updated'}, status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id='Update vendor', 
                         operation_description='Vendor partial-update endpoint',
                         request_body=VendorUpdateSerializer,
                         responses={'200': VendorUpdateSerializer()})
    def patch(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        user_id = self.request.user.id
        vendor_retrieve_validation(vendor, user_id)
        serializer = self.serializer_class_PUT(data = request.data, instance = vendor, partial = True,)
        serializer.is_valid(raise_exception=True)
        vendor_update(vendor,**serializer.validated_data)
        
        return Response({'message':'Vendor details Successfully updated'}, status.HTTP_200_OK)


class VendorListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VendorListSerializer
    queryset = Vendor.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        for query in queryset:
            query.gen_average_vendor_rating()
        serializer = self.serializer_class(queryset, many = True,)
        return Response(serializer.data, status = status.HTTP_200_OK)


class VendorDeleteView(APIView):
    permissions_classes = [IsAdmin]
    
    @swagger_auto_schema(operation_id='Delete Vendor', operation_description='Vendor delete endpoint',
                         request_body=None,
                         responses={'200': 'Vendor deleted Successfully'})
    def post(self, request, *args, **kwargs):
        vendor_id = kwargs['id']  #Name gotten from url
        vendor = get_object_or_404(Vendor.objects.all(), id= vendor_id)
        vendor_delete(vendor)
        
        return Response({'message': 'Vendor deleted Successfully'}, status = status.HTTP_200_OK)

class ScheduleCreateView(APIView):
    permissions_classes = [permissions.IsAuthenticated,] #Validation in post method doesn't allow non-owners
    serializer_class = ScheduleCreateSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        user_id = request.user.id
        #vendor = vendor_get_id(kwargs['vendor'])
        serializer.validated_data['vendor'] = kwargs['vendor'] #Vendor Id assignment
        schedule_create(user_id,**serializer.validated_data)
        
        return Response({f'message':'Schedule for has been added successfully'}, status.HTTP_201_CREATED)


class ScheduleListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleListSerializer
    
    def get_queryset(self):
        "This endpoint is only for staff schedules for all vendors"
        
        if self.request.user.is_staff != True:
            return None
        else:
            return Schedule.objects.all()

class ScheduleRetrieveListView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ScheduleRetrieveListSerializer

    def get(self, request, *args, **kwargs):
        vendor_id = kwargs['vendor']
        vendor = vendor_get_id(vendor_id)
        schedules = schedule_vendor_filter(vendor)
        for schedule in schedules:
            schedule.vendor_status()  #To refresh whether closed or open
        serializer = self.serializer_class(schedules, many = True)
        
        return Response(serializer.data, status= status.HTTP_200_OK)

class ScheduleRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleRetrieveUpdateSerializer
    
    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['vendor'])
        weekday = kwargs['weekday']
        schedule = schedule_vendor_day_filter(vendor, weekday)
        schedule.vendor_status()
        serializer = self.serializer_class(schedule)
        
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True,)
        vendor = kwargs['vendor']
        weekday = kwargs['weekday']
        schedule = schedule_vendor_day_filter(vendor, weekday)
        schedule_update(schedule, **serializer.validated_data)
        return Response({'message':'Schedule has been updated successfully'}, status = status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data,partial = True)
        serializer.is_valid(raise_exception = True,)
        vendor = kwargs['vendor']
        weekday = kwargs['weekday']
        schedule = schedule_vendor_day_filter(vendor, weekday)
        schedule_update(schedule, **serializer.validated_data)
        return Response({'message':'Schedule has been updated successfully'}, status = status.HTTP_200_OK)


class ScheduleDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
#Make changes to permissions on this endpoint and take logic to service layer
    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        schedules = schedule_vendor_filter(vendor)
        for schedule in schedules:
            schedule.delete()
        
        return Response({'message':'Schedules have been deleted successfully'}, status = status.HTTP_200_OK)

class ProductCategoryCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductCategoryCreateSerializer
    
    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        user_id = request.user.id
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        product_category_create(vendor,user_id,**serializer.validated_data)
        return Response({'message':'Product Category created successfully'}, status = status.HTTP_201_CREATED)


class ProductCategoryListView(APIView):
    permissions_classes = [permissions.AllowAny]
    serializer_class = ProductCategoryListSerializer
    
    def get(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        user_id = request.user.id
        #product_user_validation(vendor,user_id)
        product_category = product_category_ven_filter(vendor)
        serializer = self.serializer_class(product_category, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class ProductCategoryRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductCategoryRetrieveUpdateSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        vendor = kwargs['vendor']
        product_category = kwargs['slug_name']
        product_user_validation(vendor,user_id)
        data = product_category_ven_cat_filter(vendor, product_category)
        serializer = self.serializer_class(data)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_category = kwargs['slug_name']
        user_id = request.user.id
        data = product_category_ven_cat_filter(vendor, product_category)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        product_category_update(data, vendor,user_id, **serializer.validated_data)
        return Response({'message':'Product Category has been updated successfully'},
                                    status = status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_category = kwargs['slug_name']
        user_id = request.user.id
        data = product_category_ven_cat_filter(vendor, product_category)
        serializer = self.serializer_class(data = request.data, partial = True)
        serializer.is_valid(raise_exception = True)
        product_category_update(data, vendor,user_id, **serializer.validated_data)
        return Response({'message':'Product Category has been updated successfully'},
                                    status = status.HTTP_200_OK)

class ProductCategoryDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['slug_name']
        user_id = request.user.id
        product_user_validation(vendor,user_id)
        product_obj = product_category_ven_cat_filter(vendor,product_cat)

        product_category_delete(product_obj, user_id)
        return Response({'message': 'Product Category deleted Successfully'}, status = status.HTTP_200_OK)


class ProductCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductCreateSerializer
    
    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        vendor_obj = vendor_get_id(vendor)
        user_id = request.user.id
        product_user_validation(vendor, user_id)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        product_create(vendor_obj, **serializer.validated_data)
        return Response({'message':'Product has been successfully created'}, status = status.HTTP_201_CREATED)

class ProductListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()

class ProductVendorListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductVendorListSerializer
    queryset = Product.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = Product.objects.filter(vendor = kwargs['vendor'])
        serializer = self.serializer_class(queryset, many = True,)
        return Response(serializer.data, status = status.HTTP_200_OK)

class ProductRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductRetrieveUpdateSerializer

    def get(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['product_cat']
        product_name = kwargs['slug_name']
        user_id = self.request.user.id
        product_user_validation(vendor, user_id)
        product_obj = product_ven_pro_cat_slug_filter(vendor, product_cat, product_name)
        serializer = self.serializer_class(product_obj)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['product_cat']
        product_name = kwargs['slug_name']
        user_id = self.request.user.id
        product_user_validation(vendor, user_id)
        product_obj = product_ven_pro_cat_slug_filter(vendor, product_cat, product_name)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        product_update(product_obj, **serializer.validated_data)

        return Response({'message':'Product has been updated successfully'}, status = status.HTTP_200_OK)


    def patch(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['product_cat']
        product_name = kwargs['slug_name']
        user_id = self.request.user.id
        product_user_validation(vendor, user_id)
        product_obj = product_ven_pro_cat_slug_filter(vendor, product_cat, product_name)
        serializer = self.serializer_class(data = request.data, partial=True)
        serializer.is_valid(raise_exception = True)
        product_update(product_obj, **serializer.validated_data)

        return Response({'message':'Product has been updated successfully'}, status = status.HTTP_200_OK)

class ProductDeleteView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['product_cat']
        product_name = kwargs['slug_name']
        user_id = self.request.user.id
        product_user_validation(vendor, user_id)
        product_obj = product_ven_pro_cat_slug_filter(vendor, product_cat, product_name)
        product_delete(product_obj)

        return Response({'message':'Product has been deleted successfully'}, status = status.HTTP_200_OK)


class RatingCreateView(APIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = RatingCreateSerializer

    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        user_id = self.request.user.id
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        rating_create(vendor, user_id,**serializer.validated_data)
        return Response({'message':'Rating has been saved'}, status = status.HTTP_201_CREATED)


class RatingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = RatingListSerializer
    queryset = Rating.objects.all()

class RatingListUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingListUserSerializer
    queryset = Rating.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Rating.objects.filter(who_rated = self.request.user)
        serializer = self.serializer_class(queryset, many = True,)
        return Response(serializer.data, status = status.HTTP_200_OK)

class RatingRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class_GET = RatingRetrieveSerializer
    serializer_class_PUT = RatingUpdateSerializer
    
    def get(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
        serializer = self.serializer_class_GET(rating)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
        serializer = self.serializer_class_PUT(data = request.data)
        serializer.is_valid(raise_exception=True)
        rating_update(rating, **serializer.validated_data)

        return Response({'message':'Rating updated successfully'}, status = status.HTTP_200_OK)

class RatingDeleteView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
       
        rating_delete(rating)
        return Response({'message':'Rating for this vendor has been removed'}, status = status.HTTP_200_OK)

class CustomerOrderCreateView(APIView):
    permissions_classes = [permissions.AllowAny]
    serializer_class = CustomerOrderCreateSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        customer_order_create(user_id,**serializer.validated_data)
        return Response({'message':'Order added to cart'}, status = status.HTTP_201_CREATED)


class CustomerCartRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerCartRetrieveUpdateSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        cart = customer_cart_get(user)
        serializer = self.serializer_class(cart)
        return Response({'message':'Cart retrieval successful'}, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception= True)
        customer_cart_update(user,**serializer.validated_data)
        return Response({'message':'Cart updated successfully'},status = status.HTTP_200_OK)

