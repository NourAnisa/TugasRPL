from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
import math
import sqlite3
from datetime import datetime
import json
import sys, os
import time
import requests

headers = {
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

counter = 0
for i in range(242,244):

    url_topic = "https://ieeexplore.ieee.org/document/"+str(i)

    opts = webdriver.FirefoxOptions()
    opts.headless = True

    browser_driver = webdriver.Firefox(options=opts)
    browser_driver.set_window_position(-1000000, 0)
    try:
        browser_driver.get(url_topic)
    except:
        browser_driver.get(url_topic)
        time.sleep(1)   
        browser_driver.refresh()

    html_source_d = browser_driver.page_source
    soup_d = BeautifulSoup(html_source_d, "html.parser")
    browser_driver.quit()
    exist = soup_d.find("div",{"class":"document-header-title-container col"})
    if exist is not None:

        url = url_topic

        title = ""
        find_title = soup_d.find("div",{"class":"document-header-title-container col"})
        if find_title is not None:
            find_title = find_title.find("h1",{"class":"document-title text-2xl-md-lh"}).getText()
            title = find_title

        authors = ""
        find_author = soup_d.find("div",{"class":"row authors-banner-row u-flex-wrap-nowrap"})
        # print(find_author)
        if find_author is not None:
            find_author = find_author.getText()
            authors = find_author.replace(";",",")
        
        tahun_terbit = ""
        find_tahun = soup_d.find("div",{"class" : "u-pb-1 doc-abstract-pubdate"})
        # print(find_tahun)
        if find_tahun is not None :
            find_tahun = find_tahun.getText()
            find_tahun = find_tahun.replace("Date of Publication:  ","")
            print(find_tahun)
            # find_tahun = datetime.strptime(find_tahun, "%d %B %Y")
            # find_tahun = find_tahun.strftime("%Y-%m-%d")

        abstract = ""
        find_abstact = soup_d.find("div", {"class": "abstract-text row"})
        if find_abstact is not None:
            find_abstact = find_abstact.find_all("div", {"class": "u-mb-1"})
            if len(find_abstact)>0:
                print(find_abstact)
                abstract = find_abstact[0].find('div').getText()
                print(abstract)

