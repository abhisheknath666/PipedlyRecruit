from pipedlyapp.models import SemantriaItem, SemantriaCategory, SemantriaEntity, SemantriaThemes, SemantriaQuery
from pipedlyapp.singleton import Singleton

from datetime import date
import re
import logging

logger = logging.getLogger('text_analysis')

import semantria

class TextAnalysis:
    __metaclass__=Singleton

    def __init__(self):
        self.consumer_key = "1f21d381-7910-40f2-84f3-3d3caa88dd54"
        self.consumer_secret = "bce8e2a3-90ff-454e-97c2-26b6165a80eb"

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
        doc = {"id": document_id, "text": text}
        # Queues document for processing on Semantria service
        status = self.session.queueDocument(doc)
        # Check status from Semantria service
        if status == 202:
            logger.debug("%s document queued successfully.", doc["id"])
        
    def scan_for_results(self):
        status = self.session.getProcessedDocuments()
        results = []
        if isinstance(status, list):
            for object_ in status:
                results.append(object_)
        for result in results:
            self._create_item(result)

        logger.debug("Results: %s",str(results))

    def _create_item(self, result):
        doc_id = result.get("id",None)
        config_id = result.get("config_id",None)
        tag = result.get("tag",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[result.get("sentiment_polarity", "neutral")]
        sentiment_score = result.get("sentiment_score")
        document_summary = result.get("summary",None)
        source_text = result.get("source_text",None)
        status = result.get("status",None)

        if status!="processed" or doc_id==None:
            return
        
        SemantriaItem.objects.get_or_create(document_id=doc_id,source_text=source_text,tag=tag,sentiment_polarity=sentiment_polarity,document_summary=document_summary)

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
        sentiment_score = phrase.get("sentiment_score")
        is_negated = phrase.get("is_negated")
        phrase_type = PHRASE_TYPE_DICT[phrase.get("type","detected")]
            
        if not title:
            return

        SemantriaPhrase.objects.get_or_create(document_id=document_id,title=title,sentiment_polarity=sentiment_polarity,sentiment_score=sentiment_score,is_negated=is_negated,phrase_type=phrase_type)

    def _create_theme(self, document_id, theme):
        title = theme.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[theme.get("sentiment_polarity", "neutral")]
        sentiment_score = theme.get("sentiment_score")
        evidence = theme.get("evidene",None)
        is_about = theme.get("is_about",None)
        strength_score = theme.get("strength_score",None)

        if not title:
            return

        return SemantriaTheme.objects.get_or_create(document_id=document_id,title=title,sentiment_polarity=sentiment_polarity,sentiment_score=sentiment_score,evidence=evidence,is_about=is_about,strength_score=strength_score)

    def _create_entity(self, document_id, entity):
        title = entity.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[entity.get("sentiment_polarity", "neutral")]
        sentiment_score = entity.get("sentiment_score")
        evidence = entity.get("evidene",None)
        is_about = entity.get("is_about",None)
        confident = entity.get("confident",None)
        label = entity.get("label",None)
        themes = entity.get("themes",[])
        entity_type = ENTITY_TYPE_DICT[entity.get("type","named")]        

        if not title:
            return

        entity_obj = SemantriaEntity.objects.get_or_create(document_id=document_id,entity_type=entity_type,title=title,sentiment_polarity=sentiment_polarity,sentiment_score=sentiment_score,evidence=evidence,is_about=is_about,confident=confident,label=label)

        for theme in themes:
            theme_obj = self._create_theme(document_id,theme)
            SemantriaEntityToThemes.objects.get_or_create(entity=entity_obj,theme=theme_obj)

    def _create_topic(self, document_id, topic):
        title = topic.get("title",None)
        sentiment_polarity = SENTIMENT_CHOICE_DICT[topic.get("sentiment_polarity", "neutral")]
        sentiment_score = topic.get("sentiment_score")
        strength_score = topic.get("strength_score",None)
        
        
        
        
        # for data in results:
        #     # Printing of document sentiment score
        #     logger.debug("Document ", data["id"], " Sentiment score: ", data["sentiment_score"], "\r\n")

        #     # Printing of document themes
        #     if "themes" in data:
        #         logger.debug("Document themes:", "\r\n")
        #         for theme in data["themes"]:
        #             logger.debug("	", theme["title"], " (sentiment: ", theme["sentiment_score"], ")", "\r\n")

        #     # Printing of document entities
        #     if "entities" in data:
        #         logger.debug("Entities:", "\r\n")
        #         for entity in data["entities"]:
        #             logger.debug("\t",
        #                   entity["title"], " : ", entity["entity_type"],
        #                   " (sentiment: ", entity["sentiment_score"], ")", "\r\n"
        #             )
        

