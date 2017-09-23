import datetime

import pytz
from django.db.models import Count
from django.http import Http404
from push_notifications.models import GCMDevice
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdly.models import Device, Location, DeviceHistory, LocationHistory, LocationOwner
from crowdly.serializers import DeviceSerializer, LocationSerializer, ManageLocationSerializer, \
    DeviceHistorySerializer, LocationHistorySerializer

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
        # if self.request.user.is_staff:

        queryset = Location.objects.all()

        # else:
        #     logger.error("NOT STAFF")
        #     queryset = Location.objects.filter(owners__in=[self.request.user])

        queryset = queryset.annotate(owners_count=Count('owners'))
        return queryset


class ManageLocationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = ManageLocationSerializer
    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-zA-Z]{20,24}'
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Location.objects.all()
        else:
            return Location.objects.filter(owners__in=[self.request.user])

    def _get_location_from_request(self, request):
        """
        Returns device identified from the request params
        Raises exception if not found / no identifier was sent
        :param request:
        :return:
        """
        if 'uuid' in request.data.keys():

            condition = {}

            # UUID
            if 'uuid' in request.data.keys():
                uuid = request.data.get('uuid')
                condition = {'uuid': uuid}

            try:
                location = Location.objects.get(**condition)
                return location

            except Device.DoesNotExist:
                raise ManageLocationViewSet.DeviceNotFoundFromRequestException("Location not found!")
        else:
            raise ManageLocationViewSet.DeviceNotFoundFromRequestException("UUID is mandatory!")

    class LocationNotFoundFromRequestException(Exception):
        def __init__(self, message):
            super(ManageLocationViewSet.DeviceNotFoundFromRequestException, self).__init__(message)

    @list_route(methods=['post'])
    def acquire(self, request, *args, **kwargs):
        """
        Acquire by installation code
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            location = self._get_location_from_request(request)
            if self.request.user not in location.owners.all():

                locOwn = LocationOwner()
                locOwn.location = location
                locOwn.user = self.request.user

                # locOwn.operation = request.POST['operation']
                locOwn.operation = request.data.get('operation')
                # locOwn.mobile_uuid = request.POST['mobile_uuid']
                locOwn.mobile_uuid = request.data.get('mobile_uuid')
                # locOwn.threshold = int(request.POST['threshold'])
                locOwn.threshold = int(request.data.get('threshold'))
                locOwn.save()

                logger.error(str(request.data))

                # Create a FCM device
                # See if exists
                if not GCMDevice.objects.filter(registration_id=request.data.get('mobile_uuid')).exists():
                    fcm_device = GCMDevice.objects.create(registration_id=request.data.get('mobile_uuid'), cloud_message_type="FCM", user=self.request.user)

                # location.owners.add(self.request.user)
                # location.save()
                # location.add_owner_event(request.user, "Location acquired")

                logger.error("WEEEEEEEEEEEEEEEEEEEEEee")

                return Response(
                    data=LocationSerializer(location).data,
                    status=status.HTTP_200_OK,
                    content_type="application/json"
                )

            else:

                logger.error("HAAAAAAAAAAAAAAAAAAAA")

                return Response(
                    data=ManageLocationSerializer(location).data,
                    status=status.HTTP_200_OK,
                    content_type="application/json"
                )

        except ManageLocationViewSet.LocationNotFoundFromRequestException as ex:
            return Response(
                data={"message": ex.message},
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json"
            )


class ChangeDeviceViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = DeviceSerializer
    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-zA-Z]{20,24}'

    def get_queryset(self):
        return Device.objects.all()

    @detail_route(methods=['post'])
    def upd(self, request, uuid=None, **kwargs):

        try:
            device = self.get_object()
        except PermissionDenied:
            raise PermissionDenied
        except:
            raise Http404

        pp_count = request.POST['pp_count']
        device.last_people_count = pp_count
        device.last_seen = datetime.datetime.now(pytz.utc)
        device.is_online = True
        device.save()

        logger.error("PP Count: " + str(pp_count))

        # for key, val in request.POST.items():
        #     desired_state[key] = val
        #
        # device.update_desired_state(desired_state)

        return Response(
            data=DeviceSerializer(device).data,
            status=status.HTTP_200_OK,
            content_type="application/json"
        )


class DeviceHistoryViewSet(viewsets.ModelViewSet):

    class LimitedLimitOffsetPagination(LimitOffsetPagination):
        max_limit = 100

    permission_classes = (IsAuthenticated, )
    serializer_class = DeviceHistorySerializer
    pagination_class = LimitedLimitOffsetPagination
    queryset = DeviceHistory.objects.all()
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('device__uuid', 'device__serial_number')
    ordering_fields = ('__all__')
    ordering = ('-id',)


class LocationHistoryViewSet(viewsets.ModelViewSet):

    class LimitedLimitOffsetPagination(LimitOffsetPagination):
        max_limit = 100

    permission_classes = (IsAuthenticated, )
    serializer_class = LocationHistorySerializer
    pagination_class = LimitedLimitOffsetPagination
    queryset = LocationHistory.objects.all()
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('device__uuid', 'device__serial_number')
    ordering_fields = ('__all__')
    ordering = ('-id',)


class DeviceStateHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceHistorySerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = DeviceHistory.objects.all()
        query_filters = {}

        # Device
        device_uuid = self.request.query_params.get('device', None)
        if device_uuid is not None:
            query_filters['device__uuid'] = device_uuid
            # queryset = queryset.filter(device__uuid=device_uuid)

        # Last id
        last_id = self.request.query_params.get('last_id', None)
        if last_id is not None:
            query_filters['pk__gt'] = last_id

        if len(query_filters) > 0:
            queryset = queryset.filter(**query_filters)

        # Limit
        limit = self.request.query_params.get('limit', None)

        if limit:
            queryset = queryset.order_by('-created')[:limit]
        else:
            queryset = queryset.order_by('created')

        return queryset