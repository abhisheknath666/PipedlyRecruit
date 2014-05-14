from pipedlyapp.models import SemantriaItem, SemantriaPhrase, SemantriaEntity, SemantriaTheme, SemantriaOpinion, SemantriaTopic, SemantriaEntityToThemes,SENTIMENT_CHOICES, SENTIMENT_CHOICE_DICT, PHRASE_TYPE, PHRASE_TYPE_DICT, ENTITY_TYPE, ENTITY_TYPE_DICT, TOPIC_TYPE, TOPIC_TYPE_DICT, ScrapinghubItem

from pipedlyapp.web_scraper import ScrapinghubWrapper
import logging
logger = logging.getLogger("semantria_scrapinghub_relation")

class SemantriaScrapinghubUtils:
    def __init__(self):
        pass
        
    def scrapinghubitem_for_pk(self, doc_id):
        return ScrapinghubItem.objects.filter(pk=int(doc_id))

    def filter_scrapinghubitem_on_semantria_theme(self, spider_name, theme):
        filtered_scrapinghubitems = ScrapinghubWrapper().list_items(spider_name,100000)
        filtered_scrapinghubitems = ScrapinghubItem.objects.filter(pk__in=(SemantriaItem.objects.filter(semantriatheme__title__icontains=theme).values_list('document_id',flat=True)))
        return filtered_scrapinghubitems

    def filter_scrapinghubitem_on_semantria_entity(self, spider_name, entity):
        filtered_scrapinghubitems = ScrapinghubWrapper().list_items(spider_name,100000)
        filtered_scrapinghubitems = ScrapinghubItem.objects.filter(pk__in=(SemantriaItem.objects.filter(semantriaentity__title__icontains=entity).values_list('document_id',flat=True)))
        return filtered_scrapinghubitems        

    def scraped_items_not_processed_in_semantria(self):
        filtered_scrapinghubitems = ScrapinghubItem.objects.exclude(pk__in=(SemantriaItem.objects.all().values_list('document_id',flat=True)))
        return filtered_scrapinghubitems
