import json

from django.urls import reverse
from django.utils.timesince import timesince
from rest_framework import serializers

from crowdly.models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):

    last_seen_timesince = serializers.SerializerMethodField()

    def get_last_seen_timesince(self, obj):
        if obj.last_seen:
            return timesince(obj.last_seen)
        else:
            return ''

    def to_representation(self, instance):
        ret = super(DeviceSerializer, self).to_representation(instance)
        return ret

    class Meta:
        model = Device
        fields = (
            'uuid',
            'serial_number',
            'name',
            'location',
            'last_seen',
            'last_seen_timesince',
            'is_online',
            'last_people_count',
            'created',
            'modified'
        )

        read_only_fields = (
            'uuid',
            'last_seen_timesince',
            'created',
            'modified'
        )


class LocationSerializer(serializers.ModelSerializer):

    owners = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='uuid'
        )

    device_set = DeviceSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        ret = super(LocationSerializer, self).to_representation(instance)
        return ret

    class Meta:
        model = Location
        fields = (
            'uuid',
            'name',
            'latitude',
            'longitude',
            'device_set',
            'owners',
            'created',
            'modified'
        )

        read_only_fields = (
            'uuid',
            'created',
            'modified'
        )
