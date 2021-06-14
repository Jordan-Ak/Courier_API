from services.services import (schedule_create, schedule_update, vendor_create, vendor_delete, 
                               vendor_get_id, vendor_get_name, tag_create, 
                               tag_delete, vendor_get_user, vendor_update)
from services.serializers import (ScheduleCreateSerializer, ScheduleListSerializer, ScheduleRetrieveListSerializer, ScheduleRetrieveUpdateSerializer, VendorCreateSerializer, VendorListSerializer,
                                   TagCreateSerializer, TagListSerializer, 
                                   VendorRetrieveSerializer, VendorUpdateSerializer)
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.views import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Schedule, Vendor, Tag
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwner

class TagCreateView(APIView):
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]

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
    permission_classes = [permissions.IsAdminUser]
    queryset = Tag.objects.all()

class TagDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(operation_id='Delete Tag', operation_description='Tag delete endpoint',
                         request_body=None,
                         responses={'200': 'Tag deleted Successfully'})
    def post(self, request, *args, **kwargs):
        tag_select = kwargs['name'] #getting specific tag from url using tag name
        tag = get_object_or_404(Tag.objects.all(), name = tag_select)
        tag_delete(tag)
        return Response({'message':'Tag deleted successfully'}, status=status.HTTP_200_OK)


class VendorCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorCreateSerializer

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
    permission_classes = [permissions.IsAuthenticated, IsOwner,]
    serializer_class_GET = VendorRetrieveSerializer
    serializer_class_PUT = VendorUpdateSerializer

    @swagger_auto_schema(operation_id='Retrieve specific vendor',
                          operation_description='Vendor retreive endpoint',
                         request_body=None,
                         responses={'200': VendorRetrieveSerializer()})
    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        serializer = self.serializer_class_GET(vendor)
        return Response(serializer.data)

    @swagger_auto_schema(operation_id='Update vendor', operation_description='Vendor update endpoint',
                         request_body=VendorUpdateSerializer,
                         responses={'200': VendorUpdateSerializer()})
    def put(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        serializer = self.serializer_class_PUT(data = request.data, instance = vendor)
        serializer.is_valid(raise_exception=True)
        vendor_update(vendor,**serializer.validated_data)
        return Response({'message':'Vendor details Successfully updated'}, status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id='Update vendor', 
                         operation_description='Vendor partial-update endpoint',
                         request_body=VendorUpdateSerializer,
                         responses={'200': VendorUpdateSerializer()})
    def patch(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        serializer = self.serializer_class_PUT(data = request.data, instance = vendor, partial = True,)
        serializer.is_valid(raise_exception=True)
        vendor_update(vendor,**serializer.validated_data)
        return Response({'message':'Vendor details Successfully updated'}, status.HTTP_200_OK)


class VendorListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = VendorListSerializer
    #######!!!! Remember to associate the Vendor/Service to a user or not
    def get_queryset(self):
        "Restricts the queryset depending on staff or not"
        if self.request.user.is_staff != True:
            return None
        else:
            return Vendor.objects.all()


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
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleCreateSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        user_id = request.user.id
        vendor = vendor_get_id(kwargs['vendor'])
        serializer.validated_data['vendor'] = vendor.id
        schedule_create(user_id,**serializer.validated_data)
        day = serializer.validated_data['weekday']
        
        return Response({f'message':'Schedule for {day} been added successfully'}, status.HTTP_201_CREATED)


class ScheduleListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleListSerializer
    
    def get_queryset(self):
        "Restricts the queryset depending on staff or not"
        vendor_obj = Vendor.objects.filter(user = self.request.user.id)
        if self.request.user.is_staff != True:
            return Schedule.objects.filter(vendor = vendor_obj)
        else:
            return Vendor.objects.all()

class ScheduleRetrieveListView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ScheduleRetrieveListSerializer

    def get(self, request, *args, **kwargs):
        vendor_id = kwargs['vendor']
        vendor = vendor_get_id(vendor_id)
        schedule = Schedule.objects.filter(vendor = vendor)
        serializer = self.serializer_class(schedule)
        return Response(serializer.data, status= status.HTTP_200_OK)

class ScheduleRetrieveUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleRetrieveUpdateSerializer
    
    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['vendor'])
        weekday = kwargs['weekday']
        schedule = Schedule.objects.filter(vendor=vendor).filter(weekday = weekday)[0]
        serializer = self.serializer_class(schedule)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True,)
        vendor = kwargs['vendor']
        weekday = kwargs['weekday']
        schedule = Schedule.objects.filter(vendor = vendor).filter(weekday = weekday)[0]
        schedule_update(schedule, **serializer.validated_data)
        return Response({'message':'Schedule has been updated successfully'}, status = status.HTTP_200_OK)

class ScheduleDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        vendor = kwargs['vendor']
        schedules = Schedule.objects.filter(vendor = vendor)

        for schedule in schedules:
            schedule.delete()
        return Response({'message':'Schedules have been deleted successfully'}, status = status.HTTP_200_OK)