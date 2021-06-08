from services.services import tag_create
from services.serializers import TagCreateSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.views import Response
from rest_framework import status

class TagCreateView(APIView):
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception= True)
        data = serializer.validated_data
        tag_create(data['name'])
        return Response({'message':'Tag created Succesfully'}, status = status.HTTP_201_CREATED)
        
