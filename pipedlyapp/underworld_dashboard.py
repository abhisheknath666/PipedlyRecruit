from GChartWrapper import *
from pipedlyapp.models import *
from django.db import connection
from django.shortcuts import render
import json

crash_bugs_query = '''select 
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
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%)'
-- and a.title like '%stamina%'
group by a.title
having count(*) > 3
order by count(*) desc
 limit 10'''

def show_dashboard(request, name=''):
    rows = my_custom_sql(crash_bugs_query)
    values = [ tup[1] for tup in rows]
    total = reduce(lambda x,y: x+y, values)
    percentages = map(lambda p: p*100.0/total, values)
    labels = [ label[0] for label in rows ]
    # G = PieC(percentages, encoding='text')
    # G.margin(100,100,50,50)
    # G.size(600, 400)
    # G.color('6656F0')     
    # G.label(*labels)
    # return G.url
    
    context = {"percentages":json.dumps(percentages), "labels":json.dumps(labels)}
    return render(request, 'pipedly/underworld_dashboard.html', context)    

def my_custom_sql(query):
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    return rows
