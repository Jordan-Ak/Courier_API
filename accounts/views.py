from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status
from accounts.serializers import UserCreateSerializer
from accounts.services import user_create
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

