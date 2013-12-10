from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pipedlyapp.models import Poll, LinkedinProfile, ScrapinghubItem
from scrapinghub import Connection

import httplib, urllib, urllib2
import hashlib
import json
import xml.etree.ElementTree as ET

LN_CLIENT_ID = "755uojkm0y48vy"
LN_CLIENT_SECRET = "2aXh3DWAJEIYsxbc"

def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'pipedly/index.html', context)

class Singleton(type):
    """
    Metaclass that defines a singleton
    """
    _classes = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._classes:
            cls._classes[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._classes[cls]

class lnWrapper(object):
    __metaclass__ = Singleton
    def __init__(self):
        # class init
        self._access_token = ""
        self._expiration_duration = ""
        self._state = ""

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    @property
    def expiration_duration(self):
        return self._expiration_duration

    @expiration_duration.setter
    def expiration_duration(self, value):
        self._expiration_duration = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def reset_token(self):
        self._access_token = ""
        self._expiration_duration = ""

    def grab_people(self,request):
        """
        Make an api call to linkedin to retreive users matching the criteria we need
        """
        if self._access_token=="":
            return HttpResponse("Need a new access token")
        params = urllib.urlencode({ 'oauth2_access_token': self._access_token,
                                    })

        # url_string = "https://api.linkedin.com/v1/people-search?"+params
        url_string = "https://api.linkedin.com/v1/people/~/connections?"+params
        # print url_string
        connection = urllib.urlopen(url_string)

        response = connection.read()
        # print str(response)
        connections_xml = ET.fromstring(str(response))
        useful_details = ""
        for person in connections_xml.iter('person'):
            first_name = person.find('first-name').text
            last_name = person.find('last-name').text
            api_profile = person.findall('./api-standard-profile-request')
            if len(api_profile)>0:
                url = api_profile[0].find('url').text
                LinkedinProfile.objects.get_or_create(first_name=first_name,last_name=last_name,url=url)
                useful_details += "\nFirst name: "+first_name+" Last name: "+last_name+" Url: "+url
        grabbed_people = LinkedinProfile.objects.all()
        context = {'grabbed_people': grabbed_people}
        return render(request, 'pipedly/index.html', context)

    def filter_people(self, key_words):
        """
        Filter based on list of keywords
        """
        if self._access_token=="":
            return HttpResponse("Need a new access token")
        params = urllib.urlencode({ 'oauth2_access_token': self._access_token })

        if len(key_words)==0:
            return LinkedinProfile.objects.all()

        filtered_list = []
        for profile in LinkedinProfile.objects.all():
            if self.has_keywords(profile.url+"?"+params, key_words):
                filtered_list.append(profile)

        return filtered_list


    def has_keywords(self, profile_url, key_words):
        """
        Eventually we'll want to do this on another thread
        """
        profile_url = profile_url.replace("http","https")
        # print profile_url
        connection = urllib.urlopen(profile_url)
        response = connection.read()
        response_xml = ET.fromstring(str(response))
        headline = response_xml.find('./headline')
        headline_text = ""
        if headline:
            headline_text = headline.text
        for keyword in key_words:
            if headline_text.find(keyword)!=-1:
                return True
        return False

def ln_init(request):
    """
    Starts linked in authorization process
    """

    # Grab the access token from linkedln

    state = hashlib.sha224("access_token").hexdigest()
    lnWrapper().state = state
    lnWrapper().reset_token()
    params = urllib.urlencode({ 'response_type' : "code",
                                'client_id' : LN_CLIENT_ID,
                                'state' : state,
                                'redirect_uri' : 'http://127.0.0.1:8000/polls/ln/auth/' })
    url_string = "https://www.linkedin.com/uas/oauth2/authorization?"+params
    return HttpResponseRedirect(url_string)

def on_ln_authentication_response(request):
    """
    Once we get the authorization code we request for an access token
    """
    # 127.0.0.1:8000/polls/ln/auth/?code=AQTr4r9ew3tHM3D_TyLeXpnBgU-7Ugh0YtXcxlhi6lJv5Rxjw0JOh-Xv6DIPzjwfMg7FaBX4HPrHrOuTEMTl2nwJQNViBt634pFCcZiw3cjRggdZ9j8&state=ef77eccddf5ecefbb05d2218321937ff3c3de07ba4c9bc2ecae71312
    code = request.GET.get('code')
    print "Code: "+code
    state = request.GET.get('state')
    if(state==hashlib.sha224("access_token").hexdigest()):
        print "State: "+state
    else:
        print "Unknown state"

    params = urllib.urlencode({ 'grant_type':"authorization_code",
                                'code' : code,
                                'redirect_uri' : 'http://127.0.0.1:8000/polls/ln/auth/',
                                'scope' : "r_fullprofile r_network r_emailaddress",
                                'client_id' : LN_CLIENT_ID,
                                'client_secret' : LN_CLIENT_SECRET })
    url_string = "https://www.linkedin.com/uas/oauth2/accessToken?"+params
    # print url_string
    connection = urllib.urlopen(url_string, data="")

    response = connection.read()
    # expected: {"expires_in":5183999,"access_token":"AQXJCs0TreX3u8xMwh8H1926u7QCjhwwTSbgynQ65Qs7WsnTloitTPitrRF2Qczc40n1TeMgQ7Q0nPyJ72EHVqhZ8GColXZ-5j7Gnck_lzSjcv0kaV505U3OKsJqJ-JGMqOInYwYEVYgUoZ2AX1i5MWD1mgZmQ3ryFxXBc7Psi_2nNai1cQ"}
    responseJson = json.loads(response)
    expiration_duration = responseJson.get('expires_in', 0)
    access_token = responseJson.get('access_token', '')
    if expiration_duration>0 and access_token!='':
        print "Access token: "+str(access_token)+" Expiration: "+str(expiration_duration/60/60/24)
        lnWrapper().access_token = access_token
        lnWrapper().expiration_duration = expiration_duration
        return HttpResponse("Authorization success!")

    return HttpResponse("Authorization Failure!")

def grab_people(request):
    return lnWrapper().grab_people(request)

def filter_people(request):
    """
    filter people on some keywords
    """
    keywords = request.GET.get('keywords')
    keywords_list = []
    if keywords:
        keywords_list = keywords.split(' ')
    filtered_list = lnWrapper().filter_people(keywords_list)
    response = ""
    for person in filtered_list:
        response = response+" "+str(person)
    return HttpResponse(response)

# Web scraper

class ScrapinghubWrapper:
    __metaclass__=Singleton

    def __init__(self):
        self._api_key = "21822bba597f4d379d25953ba3202dfa"
        self._conn = Connection(self._api_key)
        self._cur_jobs = {}

    @property
    def api_key(self):
        return self._api_key

    def start_scheduled_job(self, spider_name):
        projects = self._conn.project_ids()
        if len(projects)<=0:
            return
        project = self._conn[projects[0]]
        if self._cur_jobs.has_key(spider_name):
            return False
        job_id = project.schedule(spider_name)
        if job_id!='':
            self._cur_jobs[spider_name] = project.job(job_id)
            return True
        return False

    def list_items(self, spider_name):
        def create_items(job):
            for item in job.items():
                ScrapinghubItem.objects.get_or_create(spider_name=spider_name, item=item)

        if self._cur_jobs.has_key(spider_name):
            job = self._cur_jobs[spider_name]
            print job.id, " ", job['state']
            if job:
                create_items(job)
        else:
            projects = self._conn.project_ids()
            if len(projects)<=0:
                return
            project = self._conn[projects[0]]
            jobs = project.jobs()
            for job in jobs:
                create_items(job)
        return ScrapinghubItem.objects.filter(spider_name=spider_name)

def start_scraping_job(request):
    """
    start a scraphub job
    """
    spider_name = request.GET.get('spider_name')
    if ScrapinghubWrapper().start_scheduled_job(spider_name):
        return HttpResponse("Success!")
    return HttpResponse("Could not start job.")

def list_scraped_items(request):
    """
    list the scrapped items for a finished job
    """
    spider_name = request.GET.get('spider_name')
    items = ScrapinghubWrapper().list_items(spider_name)
    context = { "scraped_items" : items }
    return render(request, 'pipedly/index.html', context)
