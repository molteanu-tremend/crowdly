from django.db.models import Count
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from crowdly.models import Device, Location
from crowdly.serializers import DeviceSerializer, LocationSerializer

import logging

logger = logging.getLogger('django')

class DeviceViewSet(viewsets.ModelViewSet):
    class LimitedLimitOffsetPagination(LimitOffsetPagination):
        max_limit = 100

    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-zA-Z]{20,24}'
    permission_classes = (IsAuthenticated, )
    serializer_class = DeviceSerializer
    pagination_class = LimitedLimitOffsetPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('uuid', 'serial_number', 'name')
    ordering_fields = ('__all__')
    ordering = ('uuid',)

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Device.objects.all()
        else:
            logger.error("NOT STAFF")
            queryset = Device.objects.filter(owners__in=[self.request.user])

        return queryset


class LocationViewSet(viewsets.ModelViewSet):
    class LimitedLimitOffsetPagination(LimitOffsetPagination):
        max_limit = 100

    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-zA-Z]{20,24}'
    permission_classes = (IsAuthenticated, )
    serializer_class = LocationSerializer
    pagination_class = LimitedLimitOffsetPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('uuid', 'name')
    ordering_fields = ('__all__')
    ordering = ('uuid',)

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Location.objects.all()
        else:
            logger.error("NOT STAFF")
            queryset = Location.objects.filter(owners__in=[self.request.user])

        queryset = queryset.annotate(owners_count=Count('owners'))
        return queryset

