from pipedlyapp.models import SemantriaItem, SemantriaCategory, SemantriaEntity, SemantriaThemes, SemantriaQuery

from datetime import date
import re
import logging

logger = logging.getLogger('semantria_results_organizer')

class SemantriaResultsOrganizer:
    __metaclass__=Singleton

    def __init__(self):
        pass

    def parse_into_usable_format(self):
        """        
        Retrieve items from the semantria table,
        parse them and organize them into usable
        tables.
        """
        # Estimate where to start parsing
        max_document_id = SemantriaEntity.objects.aggregate(Max('document_id'))['document_id__max']
        for semantria_item in SemantriaItem.objects.filter(document_id__gt=max_document_id):
            document_id = semantria_item.document_id
            entities = semantria_item.entities
            self._parse_and_create_entity(document_id, entities)
            queries = semantria_item.queries
            self._parse_and_create_query(document_id, queries)
            themes = semantria_item.themes
            self._parse_and_create_themes(document_id, themes)
            categories = semantria_item.categories
            self._parse_and_create_categories(document_id, categories)
        
    def _parse_and_create_entity(self, document_id, entities):
        """
        Pattern: "May 2013" is negative (sentiment score: -1.200, relevancy: 5)
        Job Title: "manager" is neutral (sentiment score: 0.500, relevancy: 5)
        Pattern: "Nov 2013" is neutral (sentiment score: 0.000, relevancy: 2)
        Quote: ""community manager!"" is neutral (sentiment score: 0.000, relevancy: 2)
        """
        entity_list = entities.split(')')
        for item in entity_list:
            item = item.lstrip()            
            entity_type_index  = self._find_index_for_pattern(item,':')
            quote_index = self._find_index_for_pattern(item, '"', entity_type_index)
            end_quote_index = item.rfind('"', quote_index)
            sentiment_start_index = self._find_index_for_pattern(item, 'is ', end_quote_index)
            sentiment_end_index = item.find(' ', sentiment_start_index)
            sentiment_score_index = self._find_index_for_pattern(item,'score: ', sentiment_end_index)
            sentiment_score_end_index = item.find(',', sentiment_score_index)
            relevancy_index = self._find_index_for_pattern(item, 'relevancy: ', sentiment_score_end_index)
            
            if entity_type_index==-1 or quote_index==-1 or end_quote_index==-1 or sentiment_start_index==-1 or sentiment_end_index==-1 or sentiment_score_index==-1 or sentiment_score_end_index==-1 or relevancy_index==-1:
                # Error parsing. Try the next item.
                continue

            entity_type = item[:entity_type_index]
            entity = item[quote_index:end_quote_index]
            sentiment = item[sentiment_start_index:sentiment_end_index]
            sentiment_score = item[sentiment_score_index:sentiment_score_end_index]
            relevancy = item[relevancy_index:]

            # Create the item
            SemantriaEntity.get_or_create(document_id=document_id, entity_type=entity_type, entity=entity, sentiment=sentiment, sentiment_score=float(sentiment_score), relevancy=int(relevancy))

    def _parse_and_create_query(self, document_id, queries):
        """
        "Business" is neutral (sentiment score: 0.430, hit count: 1)
        "Technology" is neutral (sentiment score: 0.000, hit count: 2)
        """
        queries_list = queries.split(')')
        for item in queries_list:
            item = item.lstrip()
            query_end_index = item.find(' ')
            sentiment_start_index = self._find_index_for_pattern(item, 'is ', query_end_index)
            sentiment_end_index = item.find(' ', sentiment_start_index)
            sentiment_score_index = self._find_index_for_pattern(item,'score: ', sentiment_end_index)
            sentiment_score_end_index = item.find(',', sentiment_score_index)
            hit_count_index = self._find_index_for_pattern(item, 'hit count: ', sentiment_score_end_index)
            if query_end_index==-1 or sentiment_start_index==-1 or sentiment_end_index==-1 or sentiment_score_index==-1 or sentiment_score_end_index==-1 or hit_count_index==-1:
                continue

            query = item[:query_end_index]
            sentiment = item[sentiment_start_index:sentiment_end_index]
            sentiment_score = item[sentiment_score_index:sentiment_score_end_index]
            hit_count = item[hit_count_index:]

            # Create the item
            SemantriaQuery.get_or_create(document_id=document_id, query=query, sentiment=sentiment, sentiment_score=float(sentiment_score), hit_count=int(hit_count))

    def _parse_and_create_themes(self, document_id, themes):
        """"
        "stamina refills" is positive (sentiment score: 0.784, relevancy: 7)
        "much energy" is neutral (sentiment score: 0.411, relevancy: 7)
        "crate rolls" is positive (sentiment score: 0.877, relevancy: 7)
        "corresponding equipment" is positive (sentiment score: 1.377, relevancy: 7)
        "power leveler" is neutral (sentiment score: -0.224, relevancy: 7)
        """
        themes_list = themes.split(')')
        for item in themes_list:
            item = item.lstrip()
            theme_end_index = item.find(' is')
            sentiment_start_index = self._find_index_for_pattern(item, 'is ', theme_end_index)
            sentiment_end_index = item.find(' ', sentiment_start_index)
            sentiment_score_index = self._find_index_for_pattern(item,'score: ', sentiment_end_index)
            sentiment_score_end_index = item.find(',', sentiment_score_index)
            relevancy_index = self._find_index_for_pattern(item, 'relevancy: ', sentiment_score_end_index)
            if theme_end_index==-1 or sentiment_start_index==-1 or sentiment_end_index==-1 or sentiment_score_end_index==-1 or relevancy_index==-1:
                continue

            theme = item[:theme_end_index]
            sentiment = item[sentiment_start_index:sentiment_end_index]
            sentiment_score = item[sentiment_score_index:sentiment_score_end_index]
            relevancy = item[relevancy_index:]

            SemantriaThemes.get_or_create(document_id=document_id, theme=theme, sentiment=sentiment, sentiment_score=float(sentiment_score), hit_count=int(hit_count))            

    def _parse_and_create_categories(self, document_id, categories):
        """
        "Renewable Energy" is neutral (sentiment score: 0.000, strength: 0.514)
        "Health" is neutral (sentiment score: -0.041, strength: 0.450)
        """
        category_list = categories.split(')')
        for item in categories_list:
            item = item.lstrip()
            category_end_index = item.find(' is') 
            sentiment_start_index = self._find_index_for_pattern(item, 'is ', category_end_index)
            sentiment_end_index = item.find(' ', sentiment_start_index)
            sentiment_score_index = self._find_index_for_pattern(item, 'score: ', sentiment_end_index)
            sentiment_score_end_index = item.find(',', sentiment_score_index)
            strength_index = self._find_index_for_pattern(item, 'strength: ', sentiment_score_end_index)

            if category_end_index==-1 or sentiment_start_index==-1 or sentiment_end_index==-1 or sentiment_score_index==-1 or sentiment_score_end_index==-1 or strength_index==-1:
                continue

            category_name = item[:category_end_index]
            sentiment = item[sentiment_start_index:sentiment_end_index]
            sentiment_score = item[sentiment_score_index:sentiment_score_end_index]
            strength = item[strength_index:]
            SemmantriaCategory.get_or_create(document_id=document_id, category_name=category_name, sentiment=sentiment, sentiment_score=sentiment_score, strength=strength)

    def _find_index_for_pattern(self, item, pattern, from_index=0):
        index = item.find(pattern,from_index)
        return index+len(pattern)

