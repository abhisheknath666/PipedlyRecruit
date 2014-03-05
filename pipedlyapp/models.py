from django.db import models
import datetime
from django.utils import timezone

class LinkedinProfile(models.Model):
    def __unicode__(self):
        return self.first_name+" "+self.last_name
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    class Meta:
        unique_together = ("first_name", "last_name")

class ScrapinghubItem(models.Model):
    def __unicode__(self):
        return self.spider_name
    spider_name = models.CharField(max_length=30)
    forum_post = models.TextField()
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=200)
    date = models.DateField('forum post date')

POSITIVE = 0
NEGATIVE = 1
NEUTRAL = 2
SENTIMENT_CHOICES = (
    (POSITIVE, "positive"),
    (NEGATIVE, "negative"),
    (NEUTRAL, "neutral"),
)    
SENTIMENT_CHOICE_DICT = {
    "positive":POSITIVE,
    "negative":NEGATIVE,
    "neutral":NEUTRAL,
}

class SemantriaItem(models.Model):
    def __unicode__(self):
        return self.config_id
    config_id = models.CharField(max_length=50,blank=True,null=True)
    document_id = models.OneToOneField('ScrapinghubItem')
    source_text = models.TextField(blank=True,null=True)
    tag = models.CharField(max_length=100,blank=True,null=True)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    document_summary = models.TextField(blank=True,null=True)

POSSIBLE = 0
DETECTED = 1
PHRASE_TYPE = (
    (POSSIBLE,"possible"),
    (DETECTED,"detected"),
)
PHRASE_TYPE_DICT = {
    "possible":POSSIBLE,
    "detected":DETECTED,
}
    
class SemantriaPhrase(models.Model):
    def __unicode__(self):
        return self.title
    document_id = models.ForeignKey('SemantriaItem')
    title = models.CharField(max_length=1000,blank=True,null=True)
    sentiment_score = models.FloatField(blank=True,null=True)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    is_negated = models.NullBooleanField(blank=True,null=True)
    negating_phrase = models.CharField(max_length=1000,blank=True,null=True)
    phrase_type = models.IntegerField(choices=PHRASE_TYPE,default=DETECTED,blank=True,null=True)

    class Meta:
        unique_together = ("document_id","title")

class SemantriaTheme(models.Model):
    def __unicode__(self):
        return self.theme
    document_id = models.ForeignKey('SemantriaItem')
    title = models.CharField(max_length=100)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    evidence = models.IntegerField(blank=True, null=True)
    is_about = models.NullBooleanField(blank=True,null=True)
    strength_score = models.FloatField(blank=True,null=True)

    class Meta:
        unique_together = ("document_id","title")
    

NAMED = 0
USER = 1
ENTITY_TYPE = (
    (NAMED,"named"),
    (USER,"user"),
)
ENTITY_TYPE_DICT = {
    "named":NAMED,
    "user":USER,
}

class SemantriaEntity(models.Model):
    def __unicode__(self):
        return self.entity
    document_id = models.ForeignKey('SemantriaItem')
    entity_type = models.IntegerField(choices=ENTITY_TYPE,default=NAMED,blank=True,null=True)
    title = models.CharField(max_length=100)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL,blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    evidence = models.IntegerField(blank=True, null=True)
    is_about = models.NullBooleanField(blank=True,null=True)
    confident = models.NullBooleanField(blank=True,null=True)
    label = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        unique_together = ("document_id","title")
    
class SemantriaEntityToThemes(models.Model):
    def __unicode__(self):
        return self.entity.entity
    entity = models.ForeignKey('SemantriaEntity')
    theme = models.ForeignKey('SemantriaTheme')

class SemantriaOpinion(models.Model):
    def __unicode__(self):
        return self.category_name
    document_id = models.ForeignKey('SemantriaItem')
    quotation = models.CharField(max_length=1000, blank=True, null=True)
    speaker = models.CharField(max_length=100, blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    opinion_type = models.IntegerField(choices=ENTITY_TYPE, default=NAMED, blank=True, null=True)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ("document_id","quotation")
    

CONCEPT = 0
QUERY = 1
TOPIC_TYPE = (
    (CONCEPT,"concept"),
    (QUERY,"query"),
)
TOPIC_TYPE_DICT = {
    "concept":CONCEPT,
    "query":QUERY,
}

class SemantriaTopic(models.Model):
    def __unicode__(self):
        return self.query
    document_id = models.ForeignKey('SemantriaItem')
    title = models.CharField(max_length=1000)
    topic_type = models.IntegerField(choices=TOPIC_TYPE, default=CONCEPT, blank=True, null=True)
    sentiment_polarity = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    strength_score = models.FloatField(blank=True, null=True)
    hit_count = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("document_id","title")

