import traceback
from datetime import timedelta

import shortuuid
from django.contrib.auth.models import User
from django.utils.timezone import now
from push_notifications.models import GCMDevice

from crowdly.helpers import ModelDiffMixin
from django.db import models
from django.db.models.signals import post_save, post_delete, m2m_changed
from django_extensions.db.fields import (
    ShortUUIDField, CreationDateTimeField, ModificationDateTimeField
    )
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import JSONField

import logging

logger = logging.getLogger('django')


def jsonfield_default():
    return {}




class Location(ModelDiffMixin, models.Model):

    uuid = ShortUUIDField(unique=True)

    name = models.CharField(max_length=256, blank=True, null=True)  # devName

    image = models.ImageField(null=True)

    owners = models.ManyToManyField(User, blank=True, through='LocationOwner')
    #
    latitude = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)])

    # Timestamps
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return self.name


class LocationOwner(models.Model):
    location = models.ForeignKey(Location, null=False)
    user = models.ForeignKey(User, null=False)

    operation = models.CharField(default='gt', max_length=2)
    threshold = models.IntegerField(default=0)

    mobile_uuid = models.CharField(max_length=256, null=True)

    created = CreationDateTimeField(verbose_name="Created")
    modified = ModificationDateTimeField()

    last_sent = models.DateTimeField(null=True)


class Device(ModelDiffMixin, models.Model):

    uuid = ShortUUIDField(unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)  # devName

    serial_number = models.CharField(max_length=128, blank=True, null=True, verbose_name="Serial Number")

    location = models.ForeignKey(Location)

    last_ip_address = models.GenericIPAddressField(blank=True, null=True)

    mac_address = models.CharField(max_length=128, blank=True, null=True)

    last_seen = models.DateTimeField(blank=True, null=True)

    is_online = models.BooleanField(default=False)

    last_people_count = models.IntegerField(default=0)

    # Timestamps
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    # Status
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    CHOICES_STATUS = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active')
    )
    status = models.IntegerField(
        choices=CHOICES_STATUS,
        default=STATUS_INACTIVE,
        null=False,
        blank=False)

    def save(self, *args, **kwargs):
        # Not working in Django 1.11
        dirty_fields = self.changed_fields

        # print "save :: ", self.changed_fields

        # Send notifications
        if self.pk:
            # logger.debug("------- Send save notifications")
            self._send_save_notifications(dirty_fields)

        if 'last_people_count' in dirty_fields:
            logger.error("DIRTY: " + str(dirty_fields))
            logger.error("PP: " + str(self.last_people_count))

            pp_diff = self.get_field_diff('last_people_count')
            old_pp = pp_diff[0]
            new_pp = int(pp_diff[1])

            self._save_event(old_pp, new_pp)

        if not self.pk:

            try:
                super(Device, self).save(*args, **kwargs)

                self.status = self.STATUS_ACTIVE
                self.save()
            except Exception as e:
                logger.error("XXXXXXXXXXXXXXXXXX ==> Exception!!!")
                logger.error(e)
                logger.error(traceback.format_exc())
                return
        else:
            super(Device, self).save(*args, **kwargs)

    def _save_event(self, old_pp, new_pp):

        devHist = DeviceHistory()
        devHist.device = self
        devHist.old_pp_count = old_pp
        devHist.new_pp_count = new_pp
        devHist.save()

        if self.location:
            locHist = LocationHistory()
            sumc = 0
            for dev in self.location.device_set.all():
                if dev.uuid != self.uuid:
                    sumc += dev.last_people_count
            sumc += new_pp

            locHist.location = self.location
            locHist.pp_count = sumc
            locHist.save()

            # Send Notifications to Owners
            for locOwn in self.location.locationowner_set.all():
                logger.error("WEEEEE ")
                logger.error(str(locOwn))

                if not locOwn.last_sent or (locOwn.last_sent < now() - timedelta(seconds=30)):
                    # TODO: Send push notification
                    try:
                        fcm_device = GCMDevice.objects.get(registration_id=locOwn.mobile_uuid)

                        message = self.location.name + " people count has "
                        if locOwn.operation == "lt":
                            message += "dropped below "
                            if sumc > locOwn.threshold:
                                logger.error("RET " + str(sumc) + " larger than " + str(locOwn.threshold))
                                return
                        else:
                            message += "exceeded "
                            if sumc < locOwn.threshold:
                                logger.error("RET " + str(sumc) + " lower than " + str(locOwn.threshold))
                                return
                        message += str(locOwn.threshold)
                        fcm_device.send_message(message)
                        logger.error("SENT PUSH " + message + " TO " + locOwn.mobile_uuid)
                        # TODO: Save last_sent
                        # locOwn.last_sent

                    except Exception as e:
                        logger.error("EROAAAREEEE")
                        logger.error(str(e))


    def __unicode__(self):
        return str(self.name)


    def _send_save_notifications(self, dirty_fields):

        if 'last_people_count' in dirty_fields:
            message = "Device " + str(self.uuid) + " is now " + ("online" if self.is_online else "offline")
            logger.debug("Pusher: " + message)

            # try:
            #     pusher_client.trigger('all_notifications', 'event',
            #                           {'style': "success" if self.is_online else "error", "message": message})
            # except Exception as e:
            #     logger.error("PUSHER EXCEPTION!!! " + str(e))

            logger.info("Device online state changed, now is_online " + str(self.is_online))
            self._send_alert_to_owners(message)

    def _send_alert_to_owners(self, message):
        ## send SMS
        # print "---->", settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN

        # twilio = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


        # print user.userprofile.phone
        # twilio.messages.create(
        #     # to=str(user.userprofile.phone),
        #     to="+14083918533",
        #     from_="+16507279876",
        #     body = "test alert to user " + user.username + " :: " + user.userprofile.phone
        # )

        # for owner in self.owners.all():
        #     logger.debug("Sending device status notification to : " + owner.username + ' (' + owner.email + ')')
        #
        #     try:
        #         if owner.usersetting:
        #             if owner.usersetting.sms_notifications and owner.phone:
        #                 try:
        #                     twilio.messages.create(
        #                         to=str(owner.phone),
        #                         from_="+16507279876",
        #                         body=message
        #                     )
        #                 except Exception as e:
        #                     logger.error("Phone number not ok!")
        #
        #             if owner.usersetting.email_notifications and owner.email:
        #                 ## send email
        #                 subj = "[Cloudmatix] : %s Device status changed" % owner.username
        #                 try:
        #                     mail.send_mail(
        #                         subj,
        #                         message,
        #                         'info@cloudmatix.com',
        #                         # ("afuhrmann@gmail.com",),
        #                         (owner.email,),
        #                         fail_silently=False
        #                     )
        #                 except:
        #                     print "Exception"
        #                     print traceback.print_exc(file=sys.stdout)
        #     except:
        #         print "Exception"
        #         print traceback.print_exc(file=sys.stdout)

        pass


########################################################################################


class DeviceHistory(models.Model):

    device = models.ForeignKey(Device,blank=False,
                                      on_delete=models.CASCADE,
                                      verbose_name="Device")

    old_pp_count = models.IntegerField()
    new_pp_count = models.IntegerField()

    description = models.TextField(blank=True, default='')

    # Admin
    # -----
    created = CreationDateTimeField(verbose_name="Created")
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return str(self.id)

########################################################################################


class LocationHistory(models.Model):

    location = models.ForeignKey(Location, blank=False,
                                      on_delete=models.CASCADE,
                                      verbose_name="Location")

    pp_count = models.IntegerField()

    description = models.TextField(blank=True, default='')

    # Admin
    # -----
    created = CreationDateTimeField(verbose_name="Created")
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return str(self.id)

