from services.serializers import TagCreateSerializer
from rest_framework.views import APIView
from rest_framework import permissions

class TagCreateView(APIView):
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]