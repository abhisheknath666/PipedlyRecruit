import urllib, urllib2
from pipedlyapp.singleton import Singleton
from pipedlyapp.models import ScrapinghubItem
import xml.etree.ElementTree as ET

class lnWrapper(object):
    __metaclass__ = Singleton
    def __init__(self):
        # class init
        self._access_token = ""
        self._expiration_duration = ""
        self._state = ""
        self._ln_client_id = "755uojkm0y48vy"
        self._ln_client_secret = "2aXh3DWAJEIYsxbc"

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
            break

        return filtered_list


    def has_keywords(self, profile_url, key_words):
        """
        Eventually we'll want to do this on another thread
        """
        profile_url = profile_url.replace("http","https")
        # print profile_url
        connection = urllib.urlopen(profile_url)
        response = connection.read()
        print str(response)
        response_xml = ET.fromstring(str(response))
        headline = response_xml.find('./headline')
        headline_text = ""
        if headline:
            headline_text = headline.text
        for keyword in key_words:
            if headline_text.find(keyword)!=-1:
                return True
        return False
