from django_cron import CronJobBase, Schedule
from web_scraper import ScrapinghubWrapper
from text_analysis import TextAnalysis

class ScrapinghubCronJob(CronJobBase):
    RUN_EVERY_MINS = 24*60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pipedlyapp.cron_jobs.ScrapinghubCronJob'

    def __init__(self):
        pass

    def do(self):
        ScrapinghubWrapper().grab_latest_items('underworld')
        # ScrapinghubWrapper().start_scheduled_job('underworld')

class SemantriaResultsLookupCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pipedlyapp.cron_jobs.SemantriaResultsLookupCronJob'

    def __init__(self):
        pass

    def do(self):
        TextAnalysis().scan_for_results()
    
