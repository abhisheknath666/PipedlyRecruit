from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pipedlyapp.models import Poll

import httplib, urllib
import hashlib

def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'pipedly/index.html', context)

def grab_people(request,poll_id):
    print poll_id

    # Grab the access token from linkedln

    state = hashlib.sha224("access_token").hexdigest()
    params = urllib.urlencode({ 'response_type' : "code",
                                'client_id' : "755uojkm0y48vy",
                                'state' : state,
                                'redirect_uri' : 'http://www.abhisheknath.net/ln/auth/' })
    # connection = httplib.HTTPSConnection("www.linkedin.com")
    # connection.request("POST", "/uas/oath2/authorization", params)
    # response = connection.getresponse()
    # # print response.status, response.reason
    # data = response.read()
    # # print data
    # return response
    url_string = "https://www.linkedin.com/uas/oauth2/authorization?"+params
    return HttpResponseRedirect(url_string)

def on_ln_authentication_response(request):
    code = request.GET.get('code')
    print "Token: "+code
    state = request.GET.get('state')
    if(state==hashlib.sha224("access_token").hexdigest()):
        print "State: "+state
    else:
        print "Unknown state"
    return HttpResponse('success')


        #127.0.0.1:8000/polls/ln/auth/?code=AQQjSnDitr3NQfLl8sENB8Dlg0hBPvxDeka7xrfH7ICVYKPW9CUrghXUo-6P12WQMEGjsdWg0lYus5kaxlYFT7-fnGDyWn8q0W_d50VWroMeM1GN3NU&state=ef77eccddf5ecefbb05d2218321937ff3c3de07ba4c9bc2ecae71312
