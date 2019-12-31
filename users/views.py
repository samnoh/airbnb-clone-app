import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rooms.serializers import RoomSerializer
from rooms.models import Room
from core.paginations import Pagination
from .models import User
from .serializers import UserSerializer


class UsersView(APIView):
    """
    Create an account
    """

    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(self.serializer_class(new_user).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class FavsView(APIView, Pagination):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer

    def get(self, request):
        favs = request.user.favs.all()
        page = self.paginate_queryset(favs)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    def put(self, request):
        user = request.user
        pk = request.data.get("pk", None)
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                if room in user.favs.all():
                    user.favs.remove(room)
                else:
                    user.favs.add(room)
                return Response()
            except Room.DoesNotExist:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if user is not None:
        encoded_jwt = jwt.encode(
            {"pk": user.pk}, settings.JWT_SECRET, algorithm="HS256"
        )
        return Response({"token": encoded_jwt})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
