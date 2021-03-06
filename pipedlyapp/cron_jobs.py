from django_cron import CronJobBase, Schedule
from web_scraper import ScrapinghubWrapper
from text_analysis import TextAnalysis
from pipedlyapp.models import SemantriaItem
from django.db.models import Max
from pipedlyapp.semantria_scrapinghub_relation import SemantriaScrapinghubUtils

import logging
logging.basicConfig()
logger = logging.getLogger("crons")

class ScrapinghubCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

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
    
class SendForAnalysisCronJob(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pipedlyapp.cron_jobs.SendForAnalysisCronJob'

    def __init__(self):
        pass

    def do(self):

        max_document_id = SemantriaItem.objects.aggregate(Max('document_id'))['document_id__max']
        if not max_document_id:
            max_document_id = 0

        logger.debug("Max document id: %d",max_document_id)
        scraped_objects = SemantriaScrapinghubUtils().scraped_items_not_processed_in_semantria()
        logger.debug("%s",str(scraped_objects))
        try:
            for item in scraped_objects:
                TextAnalysis().send_item_for_analysis(item.pk, item.forum_post)
        except Exception as e:
            logger.debug("%s raised",str(e))
