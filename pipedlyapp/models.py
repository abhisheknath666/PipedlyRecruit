from django.db import models
import datetime
from django.utils import timezone

class Poll(models.Model):
    def __unicode__(self):
        return self.question
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    def __unicode__(self):
        return self.choice_text
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class LinkedinProfile(models.Model):
    def __unicode__(self):
        return self.first_name+" "+self.last_name
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
