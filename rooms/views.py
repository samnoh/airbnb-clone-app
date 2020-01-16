from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.paginations import Pagination
from .models import Room
from .serializers import RoomSerializer


class RoomsView(APIView):
    serializer_class = RoomSerializer

    def get(self, request):
        paginator = Pagination()
        rooms = Room.objects.all()
        page = paginator.paginate_queryset(rooms, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = self.serializer_class(room)
            return Response(status=status.HTTP_200_OK, data=room_serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class RoomView(APIView):
    serializer_class = RoomSerializer

    def get_room(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            serializer = self.serializer_class(room)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = self.serializer_class(room, data=request.data, partial=True)
            if serializer.is_valid():
                room = serializer.save()
                return Response(self.serializer_class(room).data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            room.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def room_search(request):
    paginator = Pagination()
    rooms = Room.objects.filter()
    page = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
