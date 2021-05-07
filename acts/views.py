from django.http import JsonResponse
from django.db import transaction
from rest_framework.generics import GenericAPIView

from acts.serializers import ActSerializer
from acts.models import Act


class ActView(GenericAPIView):
    queryset = Act.objects.all()
    serializer_class = ActSerializer

    def get(self, request, *args, **krgs):
        acts = self.get_queryset()
        serializer = self.serializer_class(acts, many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    def post(self, request, *args, **krgs):
        data = request.data
        try:
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                serializer.save()
            data = serializer.data
        except Exception as e:
            data = {'error': str(e)}
        return JsonResponse(data)
