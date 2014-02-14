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

class SemantriaItem(models.Model):
    def __unicode__(self):
        return self.source_text
    configuration_id = models.CharField(max_length=50,blank=True,null=True)
    document_id = models.BigIntegerField(primary_key=True)
    source_text = models.TextField(blank=True,null=True)
    categories = models.CharField(max_length=1000,blank=True,null=True)
    entities = models.CharField(max_length=1000,blank=True,null=True)
    queries = models.CharField(max_length=100,blank=True,null=True)
    sentiment_polarity = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=100,blank=True,null=True)
    document_summary = models.TextField(blank=True,null=True)
    themes = models.CharField(max_length=1000,blank=True,null=True)

POSITIVE = 0
NEGATIVE = 1
NEUTRAL = 2
SENTIMENT_CHOICES = (
    (POSITIVE, "positive"),
    (NEGATIVE, "negative"),
    (NEUTRAL, "neutral"),
)

class SemantriaCategory(models.Model):
    def __unicode__(self):
        return self.category_name
    document_id = models.ForeignKey('SemantriaItem')
    category_name = models.CharField(max_length=100, blank=True, null=True)
    sentiment = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    strength = models.FloatField(blank=True, null=True)

class SemantriaEntity(models.Model):
    def __unicode__(self):
        return self.entity
    document_id = models.ForeignKey('SemantriaItem')
    entity_type = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    sentiment = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL,blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    relevancy = models.IntegerField(blank=True, null=True)

class SemantriaQuery(models.Model):
    def __unicode__(self):
        return self.query
    document_id = models.ForeignKey('SemantriaItem')
    query = models.CharField(max_length=100)
    sentiment = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL,blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    hit_count = models.IntegerField(blank=True, null=True)

class SemantriaThemes(models.Model):
    def __unicode__(self):
        return self.theme
    document_id = models.ForeignKey('SemantriaItem')
    theme = models.CharField(max_length=100)
    sentiment = models.IntegerField(choices=SENTIMENT_CHOICES, default=NEUTRAL, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    relevancy = models.IntegerField(blank=True, null=True)

