from cloudmatix.models import Device
from datetime import datetime, timedelta
import time

def run():


    while True:
        time_threshold = datetime.now() - timedelta(seconds=600)
        devices = Device.objects.filter(modified__lt=time_threshold)

        for device in devices:
            device.set_online(False)

        print "Set offline!"

        time.sleep(3)
