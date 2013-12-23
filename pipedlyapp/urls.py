from pipedlyapp import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^ln/$', views.ln_init, name='linkedin init'),
    url(r'^ln/auth/$', views.on_ln_authentication_response, name='Linkedin authentication response'),
    url(r'^ln/grabpeople/$', views.grab_people, name='grab people'),
    url(r'^ln/filterpeople/$', views.filter_people, name='filter people'),
    url(r'^scrape/startjob/$', views.start_scraping_job, name='start scraping job'),
    url(r'^scrape/listscrapeditems/$', views.list_scraped_items, name='list scraped items'),
    url(r'^textanalysis/getlatestdata/$', views.upload_data_for_text_analysis, name='upload data for text analysis')
)
