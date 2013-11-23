from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pipedlyapp.models import Poll, LinkedinProfile

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

class lnWrapper(object):
    access_token = ""
    expiration_duration = ""
    state = ""
    def __init__(self):
        # class init
        pass

    @classmethod
    def reset_token(cls):
        cls.access_token = ""
        cls.expiration_duration = ""

    @classmethod
    def grab_people(cls,request):
        """
        Make an api call to linkedin to retreive users matching the criteria we need
        """
        if cls.access_token=="":
            return HttpResponse("Need a new access token")
        params = urllib.urlencode({ 'oauth2_access_token': cls.access_token,
                                    })

        # url_string = "https://api.linkedin.com/v1/people-search?"+params
        url_string = "https://api.linkedin.com/v1/people/~/connections?"+params
        print url_string
        connection = urllib.urlopen(url_string)

        response = connection.read()
        print str(response)
        connections_xml = ET.fromstring(str(response))
        print connections_xml
        useful_details = ""
        for person in connections_xml.iter('person'):
            first_name = person.find('first-name').text
            last_name = person.find('last-name').text
            api_profile = person.findall('./api-standard-profile-request')
            if len(api_profile)>0:
                url = api_profile[0].find('url').text
                ln_profile = LinkedinProfile(first_name=first_name,last_name=last_name,url=url)
                ln_profile.save()
                useful_details += "\nFirst name: "+first_name+" Last name: "+last_name+" Url: "+url
        grabbed_people = LinkedinProfile.objects.all()
        context = {'grabbed_people': grabbed_people}
        return render(request, 'pipedly/index.html', context)

    @classmethod
    def filter_people(cls, key_words):
        print key_words
        return LinkedinProfile.objects.all()

def ln_init(request,poll_id):
    """
    Starts linked in authorization process
    """

    # Grab the access token from linkedln

    state = hashlib.sha224("access_token").hexdigest()
    lnWrapper.state = state
    lnWrapper.reset_token()
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
    print url_string
    connection = urllib.urlopen(url_string, data="")

    response = connection.read()
    # expected: {"expires_in":5183999,"access_token":"AQXJCs0TreX3u8xMwh8H1926u7QCjhwwTSbgynQ65Qs7WsnTloitTPitrRF2Qczc40n1TeMgQ7Q0nPyJ72EHVqhZ8GColXZ-5j7Gnck_lzSjcv0kaV505U3OKsJqJ-JGMqOInYwYEVYgUoZ2AX1i5MWD1mgZmQ3ryFxXBc7Psi_2nNai1cQ"}
    responseJson = json.loads(response)
    expiration_duration = responseJson.get('expires_in', 0)
    access_token = responseJson.get('access_token', '')
    if expiration_duration>0 and access_token!='':
        print "Access token: "+str(access_token)+" Expiration: "+str(expiration_duration/60/60/24)
        lnWrapper.access_token = access_token
        lnWrapper.expiration_duration = expiration_duration
        return HttpResponse("Authorization success!")

    return HttpResponse("Authorization Failure!")

def grab_people(request):
    return lnWrapper.grab_people(request)

def filter_people(request):
    """
    filter people on some keywords
    """
    keywords = request.GET.get('keywords')
    filtered_list = lnWrapper.filter_people(keywords)
    response = ""
    for person in filtered_list:
        response = response+" "+str(person)
    return HttpResponse(response)
