from django_cron import CronJobBase, Schedule
from .models import Link
from django.utils import timezone

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'basicapp.cron'    # a unique code

    def do(self):
        current_time = timezone.now()
        links = Link.objects.all()
        for obj in links:
            print("Checking last hit date for: ", obj.shortenURL)
            delta = current_time - obj.last_hit
            if delta.days > 2:
                print('link is older than 2 days, DELETING!')
                obj.delete()
            else:
                print('link was recently hit, Wont Delete.')

