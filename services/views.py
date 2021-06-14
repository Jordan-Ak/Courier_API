from services.services import vendor_create, vendor_delete, vendor_get_id, vendor_get_name, tag_create, tag_delete, vendor_update
from services.serializers import VendorCreateSerializer, VendorListSerializer, TagCreateSerializer, TagListSerializer, VendorRetrieveSerializer, VendorUpdateSerializer
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.views import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import Vendor, Tag
from .permissions import IsAdmin, IsOwner

class TagCreateView(APIView):
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]

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

    def post(self, request, *args, **kwargs):
        tag_select = kwargs['name'] #getting specific tag from url using tag name
        tag = get_object_or_404(Tag.objects.all(), name = tag_select)
        tag_delete(tag)
        return Response({'message':'Tag deleted successfully'}, status=status.HTTP_200_OK)


class VendorCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorCreateSerializer

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

    def get(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        serializer = self.serializer_class_GET(vendor)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        vendor = vendor_get_id(kwargs['id'])
        serializer = self.serializer_class_PUT(data = request.data, instance = vendor)
        serializer.is_valid(raise_exception=True)
        vendor_update(vendor,**serializer.validated_data)
        return Response({'message':'Vendor details Successfully updated'}, status.HTTP_200_OK)
    
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

    def post(self, request, *args, **kwargs):
        vendor_id = kwargs['id']  #Name gotten from url
        vendor = get_object_or_404(Vendor.objects.all(), id= vendor_id)
        vendor_delete(vendor)
        return Response({'message': 'Vendor deleted Successfully'}, status = status.HTTP_200_OK)