from accounts.tasks import user_email_verification_flow_sh, user_password_reset_send_sh
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from accounts.serializers import (UserAdminDetailSerializer, UserAdminListSerializer, 
                                UserCreateSerializer, 
                                UserPasswordChangeSerializer, 
                                UserPasswordResetConfirmSerializer, UserPasswordResetSerializer, 
                                UserRetrieveSerializer, UserUpdateSerializer)

from accounts.services import (user_email_verified_check, user_password_change, user_create, user_delete, user_password_reset_change,
                            user_password_reset_send, user_password_reset_validation, user_retrieve_em, 
                            user_retrieve_pass_tk, 
                            user_update, user_retrieve_pk, 
                            user_email_verification_confirm)
# Create your views here.



class UserCreateView(APIView):
    serializer_class = UserCreateSerializer

    @swagger_auto_schema(operation_id='Create a New User', operation_description='User create endpoint',
                         request_body=UserCreateSerializer,
                         responses={'200': UserCreateSerializer()})
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

    @swagger_auto_schema(operation_id='Retrieve current user', 
                         operation_description='User detail Retrieve endpoint',
                         request_body=None,
                         responses={'200': 'User retrieved successfully'})
    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserUpdateView(APIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
   
    @swagger_auto_schema(operation_id='Update Get information', 
                        operation_description='User update endpoint',
                        request_body=None,
                        responses={'200': 'User detail GET'})
    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='Update user PUT information', 
                        operation_description='User update endpoint',
                        request_body=UserUpdateSerializer,
                        responses={'200': 'User updated successfully'})
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial',False)
        serializer = self.serializer_class(data = request.data, instance = request.user,
                                                                         partial = partial)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_pk(request.user.id)
        user_update(user,**serializer.validated_data)

        return Response({'message':'User Detail Updated'},
                            status= status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_id='Update user PATCH information', 
                        operation_description='User update endpoint',
                        request_body=UserUpdateSerializer,
                        responses={'200': 'User updated successfully'})
    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data, instance = request.user,
                                                                         partial = True)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_pk(request.user.id)
        user_update(user,**serializer.validated_data)
        return Response({'message':'User Detail Updated'},
                            status= status.HTTP_200_OK)

class UserDeleteView(APIView): #Created this view to easily delete users for my convenience while developing
    #serializer_class = UserDeleteSerializer

    @swagger_auto_schema(operation_id='User Delete', 
                        operation_description='User Delete',
                        request_body=None,
                        responses={'200': 'User deleted successfully'})
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
    
    @swagger_auto_schema(operation_id='User Email verification confirm', 
                        operation_description='User email confirmation',
                        request_body=None,
                        responses={'200': 'User email is now verified'})
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model().objects.all(),
                                email_verification_token = kwargs['email_verification_token'])
        user_email_verification_confirm(user)
        
        return Response({'message':'Your email is now verified'}, status = status.HTTP_200_OK)


class UserResendEmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_id='User email verification sent', 
                        operation_description='User email verification initialized',
                        request_body=None,
                        responses={'200': 'User email verification sent succesfully'})
    def post(self, request, *args, **kwargs):
        user = request.user
        user_email_verified_check(user)
        user.generate_email_verification_token()
        user_email_verification_flow_sh.delay(user.email, user.email_verification_token)

        return Response({'message':'Email Confirmation has been sent'})

class UserPasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPasswordChangeSerializer
    
    @swagger_auto_schema(operation_id='User Password Change', 
                        operation_description='User Password Change',
                        request_body=UserPasswordChangeSerializer,
                        responses={'200': 'User password Changed Successfully'})
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        user_password_change(user,**serializer.validated_data)
        return Response({'message':'Password Changed Successfully'}, status= status.HTTP_200_OK)
        

class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer

    @swagger_auto_schema(operation_id='User Password reset sent', 
                        operation_description='User Password reset sent',
                        request_body=UserPasswordResetSerializer,
                        responses={'200': 'User Password reset sent successfully'})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_em(serializer.validated_data['email'])
       
        user.generate_password_verification_token()
        user_password_reset_send_sh.delay(user.email, user.password_reset_token)
        return Response({'message':'Password Reset sent successfully'}, status = status.HTTP_200_OK)

class UserPasswordResetConfirmView(APIView):
    serializer_class = UserPasswordResetConfirmSerializer

    @swagger_auto_schema(operation_id='User password reset input', 
                        operation_description='Password reset confirm page',
                        request_body=None,
                        responses={'200': 'Put in your new password'})
    def get(self, request, *args, **kwargs):
        user = user_retrieve_pass_tk(kwargs['password_reset_token'])
        user_password_reset_validation(user)
        return Response({'message': 'Put in you new password'}, status = status.HTTP_200_OK)

    @swagger_auto_schema(operation_id='User Password reset change', 
                        operation_description='User password reset change',
                        request_body=UserPasswordResetConfirmSerializer,
                        responses={'200': 'Password reset complete'})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = user_retrieve_pass_tk(kwargs['password_reset_token'])
        user_password_reset_change(user, serializer.validated_data['new_password'])
        return Response({'message': 'Password has been changed Successfully'}, status = status.HTTP_200_OK)


