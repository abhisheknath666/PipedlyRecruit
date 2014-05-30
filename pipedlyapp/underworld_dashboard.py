from GChartWrapper import *
from pipedlyapp.models import *
from django.db import connection
from django.shortcuts import render
import json

import logging

logger = logging.getLogger('underworld_dashboard')


churn_query = '''select a.reason, a.count from 
(select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
--and
--c.forum_post similar to '(%give up%)'
 group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
--and
-- c.forum_post similar to '(%abandon%)'
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%discontinue%)'
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(% quit %)'
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%stop playing%)'
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%give up%)'
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%abandon%)'
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%discontinue%)'
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(% quit %)'
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
-- to '(%stop playing%)'
group by a.title
having count(*) > 1
order by count desc)a 
where a.row_num <7
limit 10'''

crash_query = '''select a.reason, a.count from 
(select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%crash%)'
and position('crash' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('crash' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('crash' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%break%)'
and position('break' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('break' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('break' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%broke%)'
and position('broke' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('broke' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('broke' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(% quits %)'
and position('quits' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('quits' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('quits' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%crash%)'
and position('crash' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('crash' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('crash' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%break%)'
and position('break' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('break' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('break' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(%broke%)'
and position('broke' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('broke' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('broke' in c.forum_post))) > -200
group by a.title
having count(*) > 1
union  all
select
initcap(a.title) as reason
,count(*) as count
,row_number() OVER (ORDER BY count(*) desc) as row_num
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
a.title not in ('View Articles','Matt','Mark','Lucus')
and
c.forum_post similar to '(% quits %)'
and position('quits' in c.forum_post) >0
and ((position(a.title in c.forum_post)) - (position('quits' in c.forum_post))) < 200 
and ((position(a.title in c.forum_post)) - (position('quits' in c.forum_post))) > -200
group by a.title
having count(*) > 1)a 
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
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%|%broke%|%break%|%crash%|%bug%)')
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
c.forum_post similar to '(%quit|%abandon%|%give up%|%discontinue%|%broke%|%break%|%crash%|%bug%)')) a
group by date
-- having count(*) > 1
order by date asc
limit 10'''
 
sentiment_by_theme_query = '''(select initcap(a.theme) as Theme, a.neutral as Neutral, a.negative as Negative, a.positive as Positive from (select * from crosstab( 'select
a.title as Topic, 
case 
when a.sentiment_polarity = 2 then ''Neutral'' 
when a.sentiment_polarity = 1 then ''Negative''
when a.sentiment_polarity = 0 then ''Positive'' 
end as Sentiment, 
count(*) as Count
from pipedlyapp_semantriaentity a
     where a.title not like ''%20%''
     and a.title not like ''%Blog%''
     and a.title not like ''%#%''
     and char_length(a.title)>2
     and char_length(a.title)<20
group by
    a.title,
    a.sentiment_polarity
    order by topic') as ct(Theme varchar(255), Neutral bigint, Negative bigint, Positive bigint))a  
    order by (COALESCE(neutral,0) + COALESCE(negative,0)) desc limit 10)
 union 
 (select initcap(a.theme) as Theme, a.Neutral as Neutral, a.Negative as Negative, a.Positive as Positive from (select * from crosstab( 'select
b.theme as Topic, 
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
    and c.title not like ''%20%''
    and char_length(c.title)>2
    and char_length(c.title)<20
group by
    b.theme,
    a.sentiment_polarity
    order by theme') as ct(Theme varchar(255), Neutral bigint, Negative bigint, Positive bigint))a
  where Neutral>0 and Negative>0 and Positive>0 
  order by (COALESCE(Neutral,0) + COALESCE(Negative,0) + COALESCE(Positive,0)) desc limit 10)
   ;'''

def show_dashboard(request, name=''):
    render_data = {}
    try:
        churn_data = get_churn_data()
        render_data.update(churn_data)        
    except:
        logger.debug("Failed to get churn data")

    try:
        crash_data = get_crash_data()
        render_data.update(crash_data)
    except:
        logger.debug("Failed to get crash data")

    try:
        issues_overtime_data = get_issues_over_time()
        render_data.update(issues_overtime_data)
    except:
        logger.debug("Failed to get issues over time")

    try:
        sentiment_by_theme = get_sentiment_by_theme()
        render_data.update(sentiment_by_theme)
    except:
        logger.debug("Failed to get sentiments by theme")
        
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
