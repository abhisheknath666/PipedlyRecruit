import logging
logging.basicConfig()

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.db.models import Max

from pipedlyapp.models import SemantriaItem
from pipedlyapp.linkedin_controller import lnWrapper
from pipedlyapp.web_scraper import ScrapinghubWrapper
from pipedlyapp.text_analysis import TextAnalysis
from pipedlyapp.underworld_dashboard import *

from datetime import date
import urllib, urllib2
import hashlib
import json

logger = logging.getLogger("views")

LN_CLIENT_ID = "755uojkm0y48vy"
LN_CLIENT_SECRET = "2aXh3DWAJEIYsxbc"

def index(request):
    message = """<h3>Welcome to Pipedly.</h3><p><a href="/underworld/dashboard/?name=underworld">Click here</a> for the underworld issues dashboard.</p>"""
    return HttpResponse(message)


# Pipedly recruit use case

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

# Pipedly text analysis use case

def start_scraping_job(request):
    """
    Start a scraphub job
    http://localhost:5000/scrape/startjob?spider_name=underworld
    """
    spider_name = request.GET.get('spider_name')
    if ScrapinghubWrapper().start_scheduled_job(spider_name):
        return HttpResponse("Success!")
    return HttpResponse("Could not start job.")

def list_scraped_items(request):
    """
    list the scrapped items for a finished job
    http://localhost:5000/scrape/listscrapeditems?spider_name=underworld
    """
    spider_name = request.GET.get('spider_name')
    limit = request.GET.get('limit')
    if not limit:
        limit = 1000
    logger.debug("list_scraped_items spider_name: %s",spider_name)    
    scraped_objects = ScrapinghubWrapper().list_items(spider_name, limit)
    context = { "scraped_items" : scraped_objects }
    return render(request, 'pipedly/index.html', context)

def upload_data_for_text_analysis(request):
    """
    Save the scraped data to our text analysis database
    """
    spider_name = request.GET.get('spider_name')
    max_document_id = SemantriaItem.objects.aggregate(Max('document_id'))['document_id__max']
    if not max_document_id:
        max_document_id = 0
    scraped_objects = ScrapinghubWrapper().get_scraped_items(spider_name,max_document_id)
    response_message = "Success!"
    try:
        for item in scraped_objects:
            TextAnalysis().send_item_for_analysis(item.pk, item.forum_post)
    except Exception as e:
        response_message = "Failure " + str(e)
    return HttpResponse(response_message)

def show_underworld_dashboard(request):
    """
    Show underworld dashboard based on params
    """
    logger.debug("Underworld dashboard")
    dashboard_name = request.GET.get('name')
    
    return show_dashboard(request, dashboard_name)
    # logger.debug(url)

    # return redirect(url)
