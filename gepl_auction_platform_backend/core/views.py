# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from gepl_auction_platform_backend.core.models import Players
from gepl_auction_platform_backend.core.models import PlayerStats
from gepl_auction_platform_backend.core.models import Teams
from gepl_auction_platform_backend.core.serializers import PlayerSerializer
from gepl_auction_platform_backend.core.serializers import PlayerStatsSerializer
from gepl_auction_platform_backend.core.serializers import TeamSerializer


class TeamList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TeamDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Teams.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PlayerList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    queryset = Players.objects.all()
    serializer_class = PlayerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PlayerDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Players.objects.all()
    serializer_class = PlayerSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryPlayers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, f_format=None):
        params = {
            k: request.query_params[k]
            for k in request.query_params
            if request.query_params[k]
        }
        category = params.get("category")
        mydata = Players.objects.filter(category=category).values()
        return JsonResponse(list(mydata), safe=False)


class PlayerStatsDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, f_format=None, pk=None):
        stats_data = PlayerStats.objects.filter(player=pk).values()
        return JsonResponse(list(stats_data), safe=False)

    def post(self, request, f_format=None, pk=None):
        request_data = request.data
        request_data["player"] = pk
        serializer = PlayerStatsSerializer(data=request_data)
        # Check if data is valid
        if serializer.is_valid():
            # Save the new iten to the database serializer.save()
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors if data is invalid
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, f_format=None, pk=None):
        # Deserialize incoming 350N data s
        try:
            item = PlayerStats.objects.get(player=pk)
        except ObjectDoesNotExist:
            return JsonResponse(
                {pk: "Player does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request_data = request.data
        request_data["player"] = pk
        serializer = PlayerStatsSerializer(instance=item, data=request.data)
        # Check if data is valid
        if serializer.is_valid():
            # Save the new iten to the database serializer.save()
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors if data is invalid
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
