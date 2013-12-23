import MySQLdb
from pipedlyapp.singleton import Singleton

class RemoteTextAnalysisDB:
    """
    Class that sends parsed text to
    a remote db for text analysis
    """
    __metaclass__=Singleton
    def __init__(self):
        """
        Setup the connection
        to the remote db here
        """
        self._db = MySQLdb.connect(host='54.213.141.144',user='user01',passwd='sb02',db='zapier_feeds')
        self._cursor = self._db.cursor()
        # pp_scrape_pxg

    def send_item_to_remote_db(self, title, url, date, text):
        """
        Send a scraped item to the remote db
        """
        # print "\nSending data"+title+"\n"+url+"\n"+date.isoformat()+"\n"+text

        self._cursor.execute("""INSERT INTO pp_scrape_pxg (title, url, date, text) VALUES (%s,%s,%s,%s)""",(title,url,date.isoformat(),text))
        self._db.commit()
