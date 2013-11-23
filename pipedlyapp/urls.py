from pipedlyapp import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<poll_id>[0-9]+)/$', views.ln_init, name='linkedin init'),
    url(r'^ln/auth/$', views.on_ln_authentication_response, name='Linkedin authentication response'),
    url(r'^ln/grabpeople/$', views.grab_people, name='grab people'),
    url(r'^ln/filterpeople/$', views.filter_people, name='filter people')
)
