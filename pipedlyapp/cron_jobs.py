from django_cron import CronJobBase, Schedule
from web_scraper import ScrapinghubWrapper

class ScrapinghubCronJob(CronJobBase):
    RUN_EVERY_MINS = 120

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pipedlyapp.cron_jobs.ScrapinghubCronJob'

    def __init__(self):
        pass

    def do(self):
        ScrapinghubWrapper().list_items('underworld')
        ScrapinghubWrapper().start_scheduled_job('underworld')
