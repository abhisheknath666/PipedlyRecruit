from GChartWrapper import *
from pipedlyapp.models import *
from django.db import connection
from django.shortcuts import render
import json

churn_query = '''select a.reason, a.count from 
(select 
a.title as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
having count(*) > 1
 union
select 
a.title as reason
, count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_numa
from 
 pipedlyapp_semantriaentity a
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
group by a.title
having count(*) > 1
order by count desc)a 
where a.row_num <7
limit 10'''

crash_query = '''select a.reason, a.count from 
(select 
a.title as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
having count(*) > 1
 union
select 
a.title as reason
, count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_numa
from 
 pipedlyapp_semantriaentity a
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
 char_length(a.title)<20
 and
c.forum_post similar to '(%crash%|%break%|%brok%|%quits%)'
group by a.title
having count(*) > 1
order by count desc)a 
where a.row_num <7
limit 10'''

issues_over_time_query = '''select a.date, count(*) as count from ((select
c.date as date
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
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%)')
union all
(select
c.date as date
from
 pipedlyapp_semantriaentity a
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
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%)')) a
group by date
-- having count(*) > 1
order by date asc
limit 10'''
 
sentiment_by_theme_query = '''select * from crosstab( 'select
b.theme as Theme, 
case 
when a.sentiment_polarity = 2 then ''Neutral'' 
when a.sentiment_polarity = 1 then ''Negative'' 
WHEN a.sentiment_polarity = 0 then ''Positive'' 
end as Sentiment, 
count(*) as Count
from pipedlyapp_semantriaentity a,
    (select title as theme from pipedlyapp_semantriatheme
  group by title having count(*) >1) b, 
  pipedlyapp_semantriatheme c
    where a.document_id_id=c.document_id_id 
    and b.theme=c.title
    and c.title not like ''%Blog%''
group by
    b.theme,
    a.sentiment_polarity
  order by theme
   limit 30') as ct(Theme varchar(255), Neutral bigint, Negative bigint, Positive bigint);'''

def show_dashboard(request, name=''):
    render_data = {}
    churn_data = get_churn_data()
    crash_data = get_crash_data()
    issues_overtime_data = get_issues_over_time()
    sentiment_by_theme = get_sentiment_by_theme()
    render_data.update(churn_data)
    render_data.update(crash_data)
    render_data.update(issues_overtime_data)
    render_data.update(sentiment_by_theme)
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
    
def get_sentiment_by_theme():
    rows = my_custom_sql(sentiment_by_theme_query)
    theme = [ tup[0] for tup in rows]
    neutral = [ tup[1] for tup in rows]
    #neutral = [ 1 for tup in rows]
    negative = [ tup[2] for tup in rows]
    #negative = [ 1 for tup in rows]
    positive = [ tup[3] for tup in rows]
    #positive = [ 1 for tup in rows]
    return {"theme":json.dumps(theme), "neutral":json.dumps(neutral), "negative":json.dumps(negative), "positive":json.dumps(positive)}
    
def my_custom_sql(query):
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    return rows
