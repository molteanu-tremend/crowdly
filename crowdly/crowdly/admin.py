from django.contrib import admin


from models import Device, DeviceHistory, Location


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    # ...
    list_display = \
    ('uuid', 'name', 'serial_number', 'is_online', 'last_seen', 'last_people_count',
    'created', 'modified')
    readonly_fields = ('uuid', 'created', 'modified', 'last_seen')
    list_filter = ('is_online',)
    search_fields = ['uuid', 'serial_number', 'name']

    fieldsets = (
        (None, {
            'fields': ('uuid', 'name', 'serial_number',  'location',  'is_online', 'last_people_count',
                      'last_seen'),
        }),
        ('Admin ', {
            'fields': ('created', 'modified'),
        })
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # ...
    list_display = \
    ('uuid', 'name', 'get_owners', # 'get_last_people_count',
    'created', 'modified')
    readonly_fields = ('uuid', 'created', 'modified')
    search_fields = ['uuid', 'name']
    filter_horizontal = ('owners',)

    fieldsets = (
        (None, {
            'fields': ('uuid', 'name', 'image',
                       'latitude',  'longitude'),
        }),
        # ('Owners', {'fields': ('owners',)}),
        ('Admin ', {
            'fields': ('created', 'modified'),
        })
    )

    def get_owners(self, obj):
        return ", ".join([u.username for u in obj.owners.all()])

    # def get_owners(self, obj):
    #     return ", ".join([u.username for u in obj.owners.all()])


@admin.register(DeviceHistory)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'created', 'modified', 'description')
    readonly_fields = ('id', 'created', 'modified', )
