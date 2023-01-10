from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
import time
import sqlite3

class Acm:
    def __init__(self):
        
        # url = "https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&field1=Abstract"
        url = "https://dl.acm.org/action/doSearch?AllField=&expand=allstartPage%3D1&"
        params = {
            'ContentItemType' : 'research-article',
            'ConceptID': 118230,
            'pageSize' : 50,
            'startPage': 0,
        }
        self.url = url + urllib.parse.urlencode(params)

    def getRecord(self):
        record = 0
        opts = webdriver.FirefoxOptions()
        opts.headless = True    

        driver_web = webdriver.Firefox(options=opts)
        driver_web.set_window_position(-1000000, 0)
        driver_web.set_page_load_timeout(100000)
        driver_web.get(self.url)
        time.sleep(0.5)   
        driver_web.refresh()

        #get html page source
        html_source = driver_web.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        driver_web.quit()

        allrecords = soup.find("span", {"class": "hitsLength"})
        if allrecords is not None:
            allrecords = allrecords.getText()
            allrecords = int(allrecords.replace(',', ''))
            record = allrecords
            
        return record

    def insertPass(self):
        conn = sqlite3.connect("./database.sqlite")
        slc = conn.execute('select * from progress where (sumber=?)',['acm']).fetchone()

        if slc is None:
            record = self.getRecord()
            conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page, start_stop) values (?, ?, ?, ?, ?)",['acm',0,record,0,0])
            conn.commit()

    def updateRecord(self):
        conn = sqlite3.connect("./database.sqlite")
        slc = conn.execute('select * from progress where (sumber=?)',['acm']).fetchone()

        if slc is not None:
            init = slc[0]
            record = self.getRecord()
            if record != slc[3] :
            # conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page, start_stop) values (?, ?, ?, ?, ?)",['acm',0,record,0,0])
                conn.execute("UPDATE progress SET scrapping_record=?, last_page=? WHERE id=?", [record, 0, init])
                conn.commit()