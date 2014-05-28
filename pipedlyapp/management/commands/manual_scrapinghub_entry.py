from django.core.management.base import BaseCommand, CommandError
from pipedlyapp.models import ScrapinghubItem, SemantriaItem, SemantriaPhrase, SemantriaEntity, SemantriaTheme, SemantriaOpinion, SemantriaTopic, SemantriaEntityToThemes
from datetime import date,datetime

from django.db.models import Max

import json

class Command(BaseCommand):
    args = ''
    help = 'manually read data'

    def handle(self, *args, **options):
        def parse_date_from_string(date_str):
            # Format expected- 07-25-2013
            parsed_date = date.today()
            try:
                parsed_date = datetime.strptime(date_str,"%a, %d %B %Y").date()                    
            except:
                print "Failed to parse date"
                return parsed_date
        json_file = open(args[0],"r")
        forum_post = ""
        cur_item_index = ScrapinghubItem.objects.aggregate(Max('id'))['id__max']
        json_thread = json.load(json_file)
        for json_dict in json_thread:
            forum_post = json_dict["text"]
            title = json_dict["title"]
            url = json_dict["pageUrl"]
            parsed_date = parse_date_from_string(json_dict["date"])

            ScrapinghubItem.objects.get_or_create(spider_name="underworld", forum_post=forum_post, title=title, url=url, defaults={'date':parsed_date})
                
        

        
