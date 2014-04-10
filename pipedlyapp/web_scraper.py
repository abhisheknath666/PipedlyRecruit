import wrapped_socket_patch

from scrapinghub import Connection
from pipedlyapp.models import ScrapinghubItem
from pipedlyapp.singleton import Singleton

from datetime import date
import re
import logging
logger = logging.getLogger('web_scraper')

POST_THRESHOLD_LENGTH = 10
BOGUS_POST_SUBSTRINGS = ["Powered by vBulletin"]

class ScrapinghubWrapper:
    __metaclass__=Singleton

    def __init__(self):
        self._api_key = "b8c81c36e5ca4490859728107717f0f6"
        self._conn = Connection(self._api_key)
        self._cur_jobs = {}

    @property
    def api_key(self):
        return self._api_key

    def start_scheduled_job(self, spider_name):
        projects = self._conn.project_ids()
        if len(projects)<=0:
            return
        project = self._conn[projects[0]]
        if self._cur_jobs.has_key(spider_name):
            return False
        job_id = project.schedule(spider_name)
        if job_id!='':
            self._cur_jobs[spider_name] = project.job(job_id)
            return True
        return False

    def _prune_white_spaces(self, input_str):
        """
        Let's just prune white spaces here
        """
        input_str = input_str.replace("\t","")
        input_str = input_str.replace("\n","")
        # Prune out 4 byte characters
        try:
            # UCS-4
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # UCS-2
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
            input_str = highpoints.sub(u'\u25FD', input_str)
        return input_str

    def _is_post_redundant(self, post):
        """
        Filter on substrings to identify posts
        we don't want to save
        """
        for substring in BOGUS_POST_SUBSTRINGS:
            if post.find(substring)!=-1:
                return True

        return False

    def get_scraped_items(self, spider_name, gt_document_id=0):
        return ScrapinghubItem.objects.filter(spider_name=spider_name,pk__gt=gt_document_id)[:1000]

    def grab_latest_items(self, spider_name):
        def create_items(job):
            for item_dict in job.items():
                forum_posts = item_dict.get("forumpost",None)
                title = item_dict.get("title",None)
                url = item_dict.get("url",None)
                if not forum_posts:
                    continue
                for forum_post in forum_posts:
                    if forum_post and url and title:
                        if len(forum_post)>POST_THRESHOLD_LENGTH:
                            if self._is_post_redundant(forum_post):
                                continue
                            pruned_item = self._prune_white_spaces(forum_post)
                            # logger.debug("Pruned item: %s", pruned_item.encode('utf-8'))
                            ScrapinghubItem.objects.get_or_create(spider_name=spider_name, forum_post=pruned_item, title=title, url=url, date=date.today())
        if self._cur_jobs.has_key(spider_name):
            job = self._cur_jobs[spider_name]
            print job.id, " ", job['state']
            if job:
                try:
                    create_items(job)
                except Exception as e:
                    logger.warning('%s raised',str(e))
        else:
            projects = self._conn.project_ids()
            logger.debug("Projects: %s",str(projects))            
            if len(projects)<=0:
                return
            project = self._conn[projects[0]]
            jobs = project.jobs()
            logger.debug("Jobs: %s",str(jobs))
            for job in jobs:
                try:
                    create_items(job)
                except Exception as e:
                    logger.warning('%s raised',str(e))

    def list_items(self, spider_name, limit=1000):
        if ScrapinghubItem.objects.count()<limit:
            return ScrapinghubItem.objects.filter(spider_name=spider_name)
        return ScrapinghubItem.objects.filter(spider_name=spider_name)[0:limit]        
