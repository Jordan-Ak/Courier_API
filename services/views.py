from services.services import (cart_ordered_true, cart_product_validation, cart_user_validation, checkout_cart, checkout_create,
                               checkout_temp_create, compile_locations, customer_cart_create,
                               customer_cart_delete, customer_cart_get, customer_cart_get_id,
                               customer_cart_ordered_user_filter, customer_cart_update, final_price_calculate,
                               location_create, location_get, 
                               product_category_create, product_category_delete,
                               product_category_update, product_category_ven_cat_filter, 
                               product_category_ven_filter, product_create, product_delete, product_update, 
                               product_user_validation, product_ven_pro_cat_slug_filter,
                               rating_create, rating_delete, rating_get_id,
                               rating_update, rating_user_validation, schedule_create, 
                               schedule_update, schedule_vendor_day_filter, 
                               schedule_vendor_filter, transit_get, user_location_create,
                               user_location_get_user, user_location_validation, vendor_create, vendor_delete, 
                               vendor_get_id, vendor_get_name, tag_create, 
                               tag_delete, vendor_get_user, vendor_retrieve_validation, vendor_update)

from services.serializers import (CartCheckoutSerializer, CheckoutCreateSerializer,
                                  CustomerCartCreateSerializer,
                                  CustomerCartUserListSerializer, CustomerCartUserRetrieveSerializer,
                                  CustomerCartVendorListSerializer, LocationCreateSerializer,
                                  LocationListSerializer,
                                  ProductCategoryCreateSerializer, ProductCategoryListSerializer,
                                  ProductCategoryRetrieveUpdateSerializer, 
                                  ProductCreateSerializer, ProductListSerializer,
                                  ProductRetrieveUpdateSerializer, ProductVendorListSerializer,
                                  RatingCreateSerializer, RatingListSerializer,
                                  RatingListUserSerializer, RatingRetrieveSerializer,
                                  RatingUpdateSerializer,
                                  ScheduleCreateSerializer,ScheduleListSerializer, 
                                  ScheduleRetrieveListSerializer,
                                  ScheduleRetrieveUpdateSerializer, UserLocationCreateSerializer,
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
from .models import CustomerCart, Location, Product, ProductCategory, Rating, Schedule, Vendor, Tag
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
    
    @swagger_auto_schema(operation_id='Schedule-Create', 
                         operation_description='Schedule Create Endpoint',
                         request_body=ScheduleCreateSerializer,
                         responses={'200': 'Schedule Created Successfully'})
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

    @swagger_auto_schema(operation_id='Schedule Retrieve for Vendor', 
                         operation_description='Schedule Retrieve Endpoint for Vendor',
                         request_body=None,
                         responses={'200': ScheduleRetrieveListSerializer()})
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
    
    @swagger_auto_schema(operation_id='Schedule Retrieve endpoint', 
                         operation_description='Schedule Retrieve endpoint',
                         request_body=None,
                         responses={'200': ScheduleRetrieveUpdateSerializer()})
    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['vendor'])
        weekday = kwargs['weekday']
        schedule = schedule_vendor_day_filter(vendor, weekday)
        schedule.vendor_status()
        serializer = self.serializer_class(schedule)
        
        return Response(serializer.data, status = status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id='Schedule Retrieve Update endpoint', 
                         operation_description='Schedule Update endpoint',
                         request_body=ScheduleRetrieveUpdateSerializer(),
                         responses={'200': 'Schedule Updated Successfully'})
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True,)
        vendor = kwargs['vendor']
        weekday = kwargs['weekday']
        schedule = schedule_vendor_day_filter(vendor, weekday)
        schedule_update(schedule, **serializer.validated_data)
        return Response({'message':'Schedule has been updated successfully'}, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='Schedule Retrieve Update endpoint', 
                         operation_description='Schedule Update endpoint',
                         request_body=ScheduleRetrieveUpdateSerializer(),
                         responses={'200': 'Schedule Updated Successfully'})
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
    
    @swagger_auto_schema(operation_id='Schedule Delete', 
                         operation_description='Schedule Delete Endpoint',
                         request_body=None,
                         responses={'200': 'Schedule has been deleted successfully'})
    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        schedules = schedule_vendor_filter(vendor)
        for schedule in schedules:
            schedule.delete()
        
        return Response({'message':'Schedules have been deleted successfully'}, status = status.HTTP_200_OK)

class ProductCategoryCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductCategoryCreateSerializer
    
    @swagger_auto_schema(operation_id='Product Category Create', 
                         operation_description='Product Category Create Endpoint',
                         request_body=ProductCategoryCreateSerializer(),
                         responses={'200': 'Product Category successfully added'})
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
    
    @swagger_auto_schema(operation_id='Product Category ListView', 
                         operation_description='Product Category List View',
                         request_body=None,
                         responses={'200': ProductCategoryListSerializer()})
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


    @swagger_auto_schema(operation_id='Product Category Retrieve', 
                         operation_description='Product Category Retrieve  endpoint',
                         request_body=None,
                         responses={'200': ProductCategoryRetrieveUpdateSerializer()})
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        vendor = kwargs['vendor']
        product_category = kwargs['slug_name']
        product_user_validation(vendor,user_id)
        data = product_category_ven_cat_filter(vendor, product_category)
        serializer = self.serializer_class(data)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='Product Category Update', 
                         operation_description='Product Category Update endpoint',
                         request_body=ProductCategoryRetrieveUpdateSerializer(),
                         responses={'200': None})
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

    @swagger_auto_schema(operation_id='Product Category Update', 
                         operation_description='Product Category Update endpoint',
                         request_body=ProductCategoryRetrieveUpdateSerializer(),
                         responses={'200': None})
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


    @swagger_auto_schema(operation_id='Product Category Delete', 
                         operation_description='Product Category Delete endpoint',
                         request_body=None,
                         responses={'200': "Product Category Deleted Successfully"})
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
    
    @swagger_auto_schema(operation_id='Product Create', 
                         operation_description='Product Create endpoint',
                         request_body=ProductCreateSerializer(),
                         responses={'200': "Product Created Successfully"})
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

    @swagger_auto_schema(operation_id='Product Retrieve', 
                         operation_description='Product Retrieve endpoint',
                         request_body=None,
                         responses={'200': ProductRetrieveUpdateSerializer()})
    def get(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        product_cat = kwargs['product_cat']
        product_name = kwargs['slug_name']
        user_id = self.request.user.id
        product_user_validation(vendor, user_id)
        product_obj = product_ven_pro_cat_slug_filter(vendor, product_cat, product_name)
        serializer = self.serializer_class(product_obj)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='Product Update', 
                         operation_description='Product Update endpoint',
                         request_body=ProductRetrieveUpdateSerializer(),
                         responses={'200': "Product Updated Successfully"})
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

    @swagger_auto_schema(operation_id='Product Update', 
                         operation_description='Product Update endpoint',
                         request_body=ProductRetrieveUpdateSerializer(),
                         responses={'200': "Product Updated Successfully"})
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

    @swagger_auto_schema(operation_id='Product Delete', 
                         operation_description='Product Delete endpoint',
                         request_body=None,
                         responses={'200': "Product Deleted Successfully"})
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

    @swagger_auto_schema(operation_id='Rating Create', 
                         operation_description='Rating Create Endpoint',
                         request_body=RatingCreateSerializer,
                         responses={'200': "Rating Created Successfully"})
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
    serializer_class = RatingUpdateSerializer
    
    @swagger_auto_schema(operation_id='Rating Retrieve', 
                         operation_description='Rating Retrieve endpoint',
                         request_body=None,
                         responses={'200': RatingRetrieveSerializer()})
    def get(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
        serializer = self.serializer_class_GET(rating)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='Rating Update', 
                         operation_description='Rating Update endpoint',
                         request_body=RatingUpdateSerializer,
                         responses={'200': 'Rating Updated Successfully'})
    def put(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        rating_update(rating, user, **serializer.validated_data)

        return Response({'message':'Rating updated successfully'}, status = status.HTTP_200_OK)

class RatingDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_id='Rating Delete', 
                         operation_description='Rating Delete endpoint',
                         request_body=None,
                         responses={'200': "Rating Deleted Successfully"})
    def post(self, request, *args, **kwargs):
        rating_id = kwargs['rating']
        user = self.request.user
        rating = rating_get_id(rating_id)
        rating_user_validation(rating, user)
       
        rating_delete(rating)
        return Response({'message':'Rating for this vendor has been removed'}, status = status.HTTP_200_OK)

class CustomerCartCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = CustomerCartCreateSerializer

    ####Code That checks schedule before initiating a product
    @swagger_auto_schema(operation_id='Customer Cart Create', 
                         operation_description='Customer Cart Create endpoint',
                         request_body=CustomerCartCreateSerializer(),
                         responses={'200': "Product added to cart"})
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        cart = cart_product_validation(user, **serializer.validated_data)
        if not cart:
            customer_cart_create(user, **serializer.validated_data)
        return Response({'message':'Product Added to cart'}, status = status.HTTP_200_OK)

class CustomerCartVendorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerCartVendorListSerializer
    queryset = CustomerCart.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = None
        if self.request.user.is_staff:
            queryset = CustomerCart.objects.all()
        else:
            vendor = vendor_get_user(self.request.user)
            queryset = CustomerCart.objects.filter(vendor = vendor)
        serializer = self.serializer_class(queryset, many = True,)
        return Response(serializer.data, status = status.HTTP_200_OK)

class CustomerCartUserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerCartUserListSerializer

    @swagger_auto_schema(operation_id='CustomerCart User List Retrieve', 
                         operation_description='Customer Cart User List endpoint',
                         request_body=None,
                         responses={'200': CustomerCartUserListSerializer()})
    def get(self, request, *args, **kwargs):
        user = self.request.user
        products = customer_cart_ordered_user_filter(user)
        serializer = self.serializer_class(products, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    

class CustomerCartRetrieveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerCartUserRetrieveSerializer

    @swagger_auto_schema(operation_id='CustomerCart User Retrieve', 
                         operation_description='Customer Cart User Retrieve endpoint',
                         request_body=None,
                         responses={'200': CustomerCartUserRetrieveSerializer()})
    def get(self, request, *args, **kwargs):
        user = self.request.user
        cart_id = kwargs['cart']
        product = customer_cart_get_id(cart_id)
        cart_user_validation(user, product)
        serializer = self.serializer_class(product)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='CustomerCart User Retrieve', 
                         operation_description='Customer Cart User Retrieve endpoint',
                         request_body=CustomerCartUserRetrieveSerializer,
                         responses={'200': "Cart has been updated successfully"})
    def put(self, request, *args, **kwargs):
        user = self.request.user
        cart_id = kwargs['cart']
        product = customer_cart_get_id(cart_id)
        cart_user_validation(user, product)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        customer_cart_update(product, **serializer.validated_data)
        return Response({'message':'Cart updated Successfully'}, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='CustomerCart User Retrieve', 
                         operation_description='Customer Cart User Retrieve endpoint',
                         request_body=CustomerCartUserRetrieveSerializer,
                         responses={'200': "Cart has been updated successfully"})
    def patch(self, request, *args, **kwargs):
        user = self.request.user
        cart_id = kwargs['cart']
        product = customer_cart_get_id(cart_id)
        cart_user_validation(user, product)
        serializer = self.serializer_class(data = request.data, partial = True)
        serializer.is_valid(raise_exception = True)
        customer_cart_update(product, **serializer.validated_data)
        return Response({'message':'Cart updated Successfully'}, status = status.HTTP_200_OK)

class CustomerCartDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_id='CustomerCart Delete', 
                         operation_description='Customer Cart User Delete endpoint',
                         request_body=None,
                         responses={'200': "Product has been removed from cart."})
    def post(self, request, *args, **kwargs):
        user = self.request.user
        cart_id = kwargs['cart']
        product = customer_cart_get_id(cart_id)
        cart_user_validation(user, product)
        customer_cart_delete(product)
        return Response({'message':'Product has been removed from the cart.'}, status = status.HTTP_200_OK)


class LocationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationCreateSerializer

    @swagger_auto_schema(operation_id='Vendor Location Create', 
                         operation_description='Vendor Location Create endpoint',
                         request_body=LocationCreateSerializer(),
                         responses={'200': "A location is now associated with this vendor"})
    def post(self, request, *args, **kwargs):
        user = self.request.user
        vendor = vendor_get_user(user)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        location = location_get(**serializer.validated_data)
        location_create(user, vendor, **location)
        return Response({'message':'a location is now associated with this vendor'})

class LocationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = LocationListSerializer
    queryset = Location.objects.all()


class UserLocationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserLocationCreateSerializer

    @swagger_auto_schema(operation_id='User Location retrieve', 
                         operation_description='User Location retrieve Endpoint',
                         request_body=None,
                         responses={'200': UserLocationCreateSerializer()})
    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_location_obj = user_location_get_user(user)
        serializer = self.serializer_class(user_location_obj)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='User Location Create/Update', 
                         operation_description='User Location Create/Update Endpoint',
                         request_body=UserLocationCreateSerializer,
                         responses={'200': 'User location has been updated successfully.'})
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        formatted_address = location_get(**serializer.validated_data)
        location_exist = user_location_validation(user, **formatted_address)
        if not location_exist:
            user_location_create(user, **formatted_address)
        return Response({'message':'Your current location has been added'}, status = status.HTTP_201_CREATED)

class CheckoutCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckoutCreateSerializer
    serializer_class_product = CartCheckoutSerializer

    @swagger_auto_schema(operation_id='Checkout Retrieve', 
                         operation_description='Checkout Retrieve(retrieve all details for cart)',
                         request_body=None,
                         responses={'200': CheckoutCreateSerializer()})
    def get(self, request, *args, **kwargs):
        user = self.request.user
        cart  = checkout_cart(user)
        final_price = final_price_calculate(cart)
        user_location_obj = user_location_get_user(user)
        location_list = compile_locations(cart, user_location_obj)
        transit_dict = transit_get(location_list)
        checkout_temp_object = checkout_temp_create(final_price, user, user_location_obj.formatted_address,
                                                    **transit_dict) #temporary objects

        serializer = self.serializer_class_product(cart, many = True)
        checkout_temp_object.products = serializer.data
        serializer = self.serializer_class(checkout_temp_object)
        return Response(serializer.data, status = status.HTTP_200_OK) #Get method that reveals all the info needed for order

    @swagger_auto_schema(operation_id='Checkout Create', 
                         operation_description='Checkout Create(save all details for cart)',
                         request_body=CheckoutCreateSerializer,
                         responses={'200': "Your Products are on the way."})
    def post(self, request, *args, **kwargs):
        user = self.request.user
        cart  = checkout_cart(user)
        final_price = final_price_calculate(cart)
        user_location_obj = user_location_get_user(user)
        location_list = compile_locations(cart, user_location_obj)
        transit_dict = transit_get(location_list)
        checkout_object = checkout_create(final_price, user, user_location_obj.formatted_address,
                                                    **transit_dict) #temporary objects

        serializer = self.serializer_class_product(cart, many = True)
        checkout_object.products = serializer.data
        checkout_object.save()
        cart_ordered_true(cart)
        serializer = self.serializer_class(checkout_object)
        return Response({'message':'Order has been executed successfully'}, status = status.HTTP_200_OK)

