from pipedlyapp.models import SemantriaItem, SemantriaPhrase, SemantriaEntity, SemantriaTheme, SemantriaOpinion, SemantriaTopic, SemantriaEntityToThemes,SENTIMENT_CHOICES, SENTIMENT_CHOICE_DICT, PHRASE_TYPE, PHRASE_TYPE_DICT, ENTITY_TYPE, ENTITY_TYPE_DICT, TOPIC_TYPE, TOPIC_TYPE_DICT
from pipedlyapp.singleton import Singleton
from pipedlyapp.semantria_scrapinghub_relation import SemantriaScrapinghubUtils

from datetime import date
import re
import logging

logger = logging.getLogger('text_analysis')

import semantria

class TextAnalysis:
    __metaclass__=Singleton

    def __init__(self):
        self.consumer_key = "aba68dad-ab33-466b-96ee-e1fde210afea"
        self.consumer_secret = "4c861b1b-ef9f-4c69-9dca-2ba3c3efbe33"

        # Creates JSON serializer instance
        serializer = semantria.JsonSerializer()
        # Initializes new session with the serializer object and the keys.
        self.session = semantria.Session(self.consumer_key, self.consumer_secret, serializer, use_compression=True)

        # Initialize session callback handlers
        #self.session.Request += self._onRequest
        #self.session.Response += self._onResponse
        self.session.Error += self._onError
        #self.session.DocsAutoResponse += self._onDocsAutoResponse
        #self.session.CollsAutoResponse += self._onCollsAutoResponse

    def _onRequest(self, sender, result):
        print("\n", "REQUEST: ", result)


    def _onResponse(self, sender, result):
        print("\n", "RESPONSE: ", result)


    def _onError(self, sender, result):
        print("\n", "ERROR: ", result)


    def _onDocsAutoResponse(self, sender, result):
        print("\n", "AUTORESPONSE: ", len(result), result)


    def _onCollsAutoResponse(self, sender, result):
        print("\n", "AUTORESPONSE: ", len(result), result)

    def send_item_for_analysis(self, document_id, text):
        doc = {"id": str(document_id), "text": text[:8000]}
        # Queues document for processing on Semantria service
        status = self.session.queueDocument(doc)
        # Check status from Semantria service        
        if status == 202:
            logger.debug("%s document queued successfully.", doc["id"])
        
    def scan_for_results(self):
        logger.debug("Scanning for results")
        status = self.session.getProcessedDocuments()
        results = []
        if isinstance(status, list):
            for object_ in status:
                results.append(object_)
        for result in results:
            self._create_item(result)

        # logger.debug("Results: %s",str(results))

    def _create_item(self, result):
        doc_id = int(result.get("id",None))
        config_id = result.get("config_id",None)
        tag = result.get("tag",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[result.get("sentiment_polarity", "neutral")]
        sentiment_score = result.get("sentiment_score")
        document_summary = result.get("summary",None)
        source_text = result.get("source_text",None)
        status = result.get("status",None)


        try:
            logger.debug("doc_id: %s config_id: %s tag: %s sentiment_polarity: %s sentiment_score: %s document_summary: %s source_text: %s status: %s", str(doc_id), str(config_id), str(tag), str(sentiment_polarity), str(sentiment_score), str(document_summary), str(source_text), str(status))
        except Exception as e:
            logger.debug("Failed to log created item: %s", str(e))
        
        success = True
        if status!="PROCESSED":
            success=False
        if doc_id!=None:
            doc_id = SemantriaScrapinghubUtils().scrapinghubitem_for_pk(doc_id)
            if doc_id==None:
                success=False
        else:
            success=False

        if not success:
            logger.debug("Problem creating item")
            return
                
        doc_id, created = SemantriaItem.objects.get_or_create(document_id=doc_id[0], defaults={'config_id':config_id, 'source_text':source_text,'tag':tag,'sentiment_polarity':sentiment_polarity,'sentiment_score':sentiment_score,'document_summary':document_summary})
        logger.debug("Results: %s",str(SemantriaItem.objects.all()))

        phrases = result.get("phrases",[])
        for phrase in phrases:
            self._create_phrase(doc_id,phrase)

        themes = result.get("themes",[])
        for theme in themes:
            self._create_theme(doc_id,theme)

        entities = result.get("entities",[])
        for entity in entities:
            self._create_entity(doc_id,entity)

    def _create_phrase(self, document_id, phrase):
        title = phrase.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[phrase.get("sentiment_polarity", "neutral")]
        sentiment_score = phrase.get("sentiment_score",None)
        is_negated = phrase.get("is_negated",None)
        phrase_type = PHRASE_TYPE_DICT[phrase.get("type","detected")]
            
        if not title:
            logger.debug("Problem creating phrase")            
            return

        SemantriaPhrase.objects.get_or_create(document_id=document_id,title=title,defaults={'sentiment_polarity':sentiment_polarity,'sentiment_score':sentiment_score,'is_negated':is_negated,'phrase_type':phrase_type})

    def _create_theme(self, document_id, theme):
        title = theme.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[theme.get("sentiment_polarity", "neutral")]
        sentiment_score = theme.get("sentiment_score")
        evidence = theme.get("evidene",None)
        is_about = theme.get("is_about",None)
        strength_score = theme.get("strength_score",None)

        if not title:
            logger.debug("Problem creating theme")            
            return

        return SemantriaTheme.objects.get_or_create(document_id=document_id,title=title,defaults={'sentiment_polarity':sentiment_polarity,'sentiment_score':sentiment_score,'evidence':evidence,'is_about':is_about,'strength_score':strength_score})

    def _create_entity(self, document_id, entity):
        title = entity.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[entity.get("sentiment_polarity", "neutral")]
        sentiment_score = entity.get("sentiment_score",None)
        evidence = entity.get("evidene",None)
        is_about = entity.get("is_about",None)
        confident = entity.get("confident",None)
        label = entity.get("label",None)
        themes = entity.get("themes",[])
        entity_type = ENTITY_TYPE_DICT[entity.get("type","named")]        

        if not title:
            logger.debug("Problem creating entity")            
            return

        entity_obj, created = SemantriaEntity.objects.get_or_create(document_id=document_id,title=title, defaults={'entity_type':entity_type,'sentiment_polarity':sentiment_polarity,'sentiment_score':sentiment_score,'evidence':evidence,'is_about':is_about,'confident':confident,'label':label})

        for theme in themes:
            theme_obj, created = self._create_theme(document_id,theme)
            SemantriaEntityToThemes.objects.get_or_create(entity=entity_obj,theme=theme_obj)

    def _create_topic(self, document_id, topic):
        title = topic.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[topic.get("sentiment_polarity", "neutral")]
        sentiment_score = topic.get("sentiment_score",None)
        strength_score = topic.get("strength_score",None)
        topic_type = TOPIC_TYPE_DICT[topic.get("type","query")]
        hit_count = topic.get("hitcount",None)

        if not title:
            logger.debug("Problem creating topic")                        
            return

        SemantriaTopic.objects.get_or_create(document_id=document_id,title=title,defaults={'topic_type':topic_type,'sentiment_polarity':sentiment_polarity,'sentiment_score':sentiment_score,'strength_score':strength_score,'hit_count':hit_count})        
