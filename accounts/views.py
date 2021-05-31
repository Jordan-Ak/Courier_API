from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from django.contrib.auth import get_user_model

from accounts.serializers import (UserAdminDetailSerializer, UserAdminListSerializer, 
                                UserCreateSerializer, UserDeleteSerializer, 
                                UserRetrieveSerializer, UserUpdateSerializer)
from accounts.services import (user_create, user_delete, user_retrieve_em, 
                            user_update, user_retrieve_pk, 
                            user_email_verification_confirm,user_email_verification_flow)
# Create your views here.



class UserCreateView(APIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        
        data = serializer.validated_data
        user_create(data['email'], data['first_name'],data['last_name'],data['phone_no'], data['password'])
        return Response({'message':'User Created Successfully, verify your email'},
                            status= status.HTTP_201_CREATED)


class UserRetrieveView(APIView):
    serializer_class = UserRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserUpdateView(APIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial',False)
        serializer = self.serializer_class(data = request.data, instance = request.user,
                                                                         partial = partial)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_pk(request.user.id)
        user_update(user,**serializer.validated_data)

        return Response({'message':'User Detail Updated'},
                            status= status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data, instance = request.user,
                                                                         partial = True)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_pk(request.user.id)
        user_update(user,**serializer.validated_data)
        return Response({'message':'User Detail Updated'},
                            status= status.HTTP_200_OK)

class UserDeleteView(APIView):
    serializer_class = UserDeleteSerializer

    def post(self, request, *args, **kwargs):
        user = user_retrieve_em(kwargs['email'])
        user_delete(user)
        return Response({'message':'Account Deleted'},
                            status= status.HTTP_200_OK)


class UserAdminListView(generics.ListAPIView):
    serializer_class = UserAdminListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserAdminDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()
    lookup_url_kwarg = 'id'

class UserEmailVerificationConfirmView(APIView):
    
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model().objects.all(),
                                email_verification_token = kwargs['email_verification_token'])
        user_email_verification_confirm(user)
        
        return Response({'message':'Your email is now verified'}, status = status.HTTP_200_OK)


class UserResendEmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
#This view has minimal business logic within
    def post(self, request, *args, **kwargs):
        user = request.user
        user_email_verification_flow(user)

        return Response({'message':'Email Confirmation has been sent'})