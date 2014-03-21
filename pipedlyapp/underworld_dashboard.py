from GChartWrapper import *
from pipedlyapp.models import *
from django.db import connection

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
 c.forum_post like '%crash%'
 and
 char_length(a.title)>2
group by a.title
 having count(*) > 4
union 
select 
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
 c.forum_post like '%bug%'
 and
 char_length(a.title)>2
group by a.title
 having count(*) > 4
limit 10'''

def show_dashboard(name=''):
    rows = my_custom_sql(crash_bugs_query)
    values = [ tup[1] for tup in rows]
    total = reduce(lambda x,y: x+y, values)
    percentages = map(lambda p: p*100.0/total, values)
    labels = [ label[0] for label in rows ]
    G = Pie3D(percentages, encoding='text')
    G.size(300,100)
    G.color('F00000')     
    G.label(*labels)
    return G.url

def my_custom_sql(query):
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    return rows
