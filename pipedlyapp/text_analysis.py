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

        logger.debug("Results: %s",str(results))

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
        

