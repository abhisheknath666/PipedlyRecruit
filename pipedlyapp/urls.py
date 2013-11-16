from pipedlyapp import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<poll_id>[0-9]+)/$', views.grab_people, name='grab people'),
    # url(r'^linkedin/?code=(?P<code>[-\w\d\_]+)&state=(?P<state>[-\w\d\_]+)/$', views.on_ln_authentication_response, name='Linkedin authentication response') 
    url(r'^ln/auth/$', views.on_ln_authentication_response, name='Linkedin authentication response')
)
