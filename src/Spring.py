import sqlite3
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
import math
from datetime import datetime
import json
import sys, os
import time
import requests

class Spring:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    def getTotalPageAndRecord(self,kategori="totalpage"):    
        totalPage = 0
        record = 0
        page = 1
        
        url = "https://link.springer.com/search/page/"+str(page)+'?query=&facet-content-type="Article"'
        opts = webdriver.FirefoxOptions()
        opts.headless = True
        browser_driver = webdriver.Firefox(options=opts)
        browser_driver.set_window_position(-1000000, 0)
        try:
            browser_driver.get(url)
        except:
            browser_driver.get(url)
            time.sleep(1)   
            browser_driver.refresh()

        html_source_d = browser_driver.page_source
        soup_d = BeautifulSoup(html_source_d, "html.parser")
        browser_driver.quit()
        if soup_d is not None:
            if kategori == 'totalpage':
                find_total = soup_d.find_all("span", {"class": "number-of-pages"})
                if find_total is not None:
                    totalPage = find_total[0].getText()
                    totalPage = int(totalPage.replace(',', ''))
            else:
                find_total_record = soup_d.find_all("h1", {"id": "number-of-search-results-and-search-terms"})
                if find_total_record is not None:
                    # print()
                    record = find_total_record[0].find('strong').getText()
                    record = int(record.replace(',', ''))

        if kategori == 'totalpage':
            return totalPage
        else:
            return record

    def insertPass(self):
        conn = sqlite3.connect("./database.sqlite")
        slc = conn.execute('select * from progress where (sumber=?)',['spring']).fetchone()

        if slc is None:
            record = self.getTotalPageAndRecord('record')
            conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page, start_stop) values (?, ?, ?, ?, ?)",['spring',0,record,1,0])
            conn.commit()

    def updateRecord(self):
        conn = sqlite3.connect("./database.sqlite")
        slc = conn.execute('select * from progress where (sumber=?)',['spring']).fetchone()

        if slc is not None:
            init = slc[0]
            record = self.getTotalPageAndRecord('record')
            if record != slc[3] :
            # conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page, start_stop) values (?, ?, ?, ?, ?)",['acm',0,record,0,0])
                conn.execute("UPDATE progress SET scrapping_record=?, last_page=? WHERE id=?", [record, 0, init])
                conn.commit()