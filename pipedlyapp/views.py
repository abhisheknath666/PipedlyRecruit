from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pipedlyapp.models import Poll

import httplib, urllib, urllib2
import hashlib

LN_CLIENT_ID = "755uojkm0y48vy"
LN_CLIENT_SECRET = "2aXh3DWAJEIYsxbc"

def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'pipedly/index.html', context)

def grab_people(request,poll_id):
    print poll_id

    # Grab the access token from linkedln

    state = hashlib.sha224("access_token").hexdigest()
    params = urllib.urlencode({ 'response_type' : "code",
                                'client_id' : LN_CLIENT_ID,
                                'state' : state,
                                'redirect_uri' : 'http://www.abhisheknath.net/ln/auth/' })
    url_string = "https://www.linkedin.com/uas/oauth2/authorization?"+params
    return HttpResponseRedirect(url_string)

def on_ln_authentication_response(request):
    #{"expires_in":5183999,"access_token":"AQXJCs0TreX3u8xMwh8H1926u7QCjhwwTSbgynQ65Qs7WsnTloitTPitrRF2Qczc40n1TeMgQ7Q0nPyJ72EHVqhZ8GColXZ-5j7Gnck_lzSjcv0kaV505U3OKsJqJ-JGMqOInYwYEVYgUoZ2AX1i5MWD1mgZmQ3ryFxXBc7Psi_2nNai1cQ"}
    code = request.GET.get('code')
    print "Code: "+code
    state = request.GET.get('state')
    if(state==hashlib.sha224("access_token").hexdigest()):
        print "State: "+state
    else:
        print "Unknown state"

    params = urllib.urlencode({ 'grant_type':"authorization_code",
                                'code' : code,
                                'redirect_uri' : 'http://www.abhisheknath.net/ln/auth/',
                                'client_id' : LN_CLIENT_ID,
                                'client_secret' : LN_CLIENT_SECRET })
    url_string = "https://www.linkedin.com/uas/oauth2/accessToken?"+params
    print url_string
    connection = urllib.urlopen(url_string, data="")
    return HttpResponse(connection.read())
