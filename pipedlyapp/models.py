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

class SemmantriaItem(models.Model):
    def __unicode__(self):
        return self.source_text
    configuration_id = models.CharField(max_length=50)
    document_id = models.CharField(max_length=50)
    source_text = models.TextField()
    categories = models.CharField(max_length=100)
    entities = models.CharField(max_length=100)
    queries = models.CharField(max_length=100)
    sentiment_polarity = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    document_summary = models.CharField(max_length=1000)
    themes = models.CharField(max_length=1000)
    
