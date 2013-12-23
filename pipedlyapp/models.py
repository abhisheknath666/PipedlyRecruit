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
