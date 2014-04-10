from GChartWrapper import *
from pipedlyapp.models import *
from django.db import connection
from django.shortcuts import render
import json

churn_query = '''select 
a.title as theme
, count(*)
from 
 pipedlyapp_semantriatheme a
,pipedlyapp_semantriaitem b
, pipedlyapp_scrapinghubitem c
where 
a.document_id_id= b.id
and
b.document_id_id=c.id
and 
a.title not like '%20%'
 and
 b.sentiment_polarity = 1
 and
 char_length(a.title)>2
 and
c.forum_post similar to '(%quit%|%abandon%|%give up%|%discontinue%)'
group by a.title
having count(*) > 3
order by count(*) desc
 limit 10'''

crash_query = '''select 
a.title as theme
, count(*)
from 
 pipedlyapp_semantriatheme a
,pipedlyapp_semantriaitem b
, pipedlyapp_scrapinghubitem c
where 
a.document_id_id= b.id
and
b.document_id_id=c.id
and 
a.title not like '%20%'
 and
 b.sentiment_polarity = 1
 and
 char_length(a.title)>2
 and
c.forum_post similar to '(%crash%|%break%|%brok%|%quits%)'
group by a.title
having count(*) > 3
order by count(*) desc
 limit 10'''

issues_over_time_query = '''select
c.date as date
, count(*)
from
 pipedlyapp_semantriatheme a
,pipedlyapp_semantriaitem b
, pipedlyapp_scrapinghubitem c
where
a.document_id_id= b.id
and
b.document_id_id=c.id
and
a.title not like '%20%'
 and
 b.sentiment_polarity = 1
 and
 char_length(a.title)>2
 and
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%)'
group by c.date
having count(*) > 3
order by count(*) desc
 limit 10'''

def show_dashboard(request, name=''):
    render_data = {}
    churn_data = get_churn_data()
    crash_data = get_crash_data()
    issues_overtime_data = get_issues_over_time()
    render_data.update(churn_data)
    render_data.update(crash_data)
    render_data.update(issues_overtime_data)
    return render(request, 'pipedly/underworld_dashboard.html', render_data)

def get_churn_data():
    rows = my_custom_sql(churn_query)
    values = [ tup[1] for tup in rows]
    total = reduce(lambda x,y: x+y, values)
    percentages = map(lambda p: p*100.0/total, values)
    labels = [ label[0] for label in rows ]
    return {"churn_percentages":json.dumps(percentages), "churn_labels":json.dumps(labels)}

def get_crash_data():
    rows = my_custom_sql(crash_query)
    values = [ tup[1] for tup in rows]
    total = reduce(lambda x,y: x+y, values)
    percentages = map(lambda p: p*100.0/total, values)
    labels = [ label[0] for label in rows ]
    return {"crash_percentages":json.dumps(percentages), "crash_labels":json.dumps(labels)}

def get_issues_over_time():
    rows = my_custom_sql(issues_over_time_query)
    counts = [ tup[1] for tup in rows]
    dates = [ label[0] for label in rows ]
    dthandler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
        else "")
    return {"counts":json.dumps(counts), "dates":json.dumps(dates, default=dthandler)}
    
def my_custom_sql(query):
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    return rows
