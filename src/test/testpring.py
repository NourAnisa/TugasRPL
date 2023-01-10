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


def getTotalPageAndRecord(kategori="totalpage"):    
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


def scrap():
    totalPage = getTotalPageAndRecord(kategori="totalpage")

    for page in range(1,totalPage,1):
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
            find_lists = soup_d.find("ol", {"id": "results-list"})
            if len(find_lists) > 0:
                for lists in find_lists:
                    link = lists.find('h2')
                    if link is not None:
                        link = link.find('a',href=True).get("href")
                        link = "https://link.springer.com"+link
                        ## visit link

                        opts_de = webdriver.FirefoxOptions()
                        opts_de.headless = True
                        browser_driver_de = webdriver.Firefox(options=opts_de)
                        browser_driver_de.set_window_position(-1000000, 0)
                        try:
                            browser_driver_de.get(link)
                        except:
                            browser_driver_de.get(link)
                            time.sleep(1)   
                            browser_driver_de.refresh()

                        html_source_de = browser_driver_de.page_source
                        soup_de = BeautifulSoup(html_source_de, "html.parser")
                        browser_driver_de.quit()
                        if soup_de is not None:
                            url_ = link                            
                            tahun_terbit = ""
                            find_tahun = soup_de.find("div",{"class" :"c-article-header"})
                            if find_tahun is not None:
                                find_tahun = find_tahun.find("time").getText()
                                tahun_terbit = find_tahun
                            
                            title = ""
                            find_title = soup_de.find("div",{"class" :"c-article-header"})
                            if find_title is not None:
                                find_title = find_title.find("h1",{"class" : "c-article-title"}).getText()
                                title = find_title
                                          
                            authors = ""
                            find_authors = soup_de.find("div",{"class" :"c-article-header"})
                            if find_authors is not None:
                                find_authors = find_authors.find("ul",{"class" : "c-article-author-list c-article-author-list--short js-no-scroll"})
                                if find_authors is not None:
                                    find_authors = find_authors.find_all("li",{"class":"c-article-author-list__item"})
                                    for author in find_authors:
                                        author = author.find('a').getText()
                                        if len(authors)> 0:
                                            authors = authors +", "+ author
                                        else:
                                            authors = authors + author
                                          
                            abstract = ""
                            find_abstract = soup_de.find("div",{"class" :"c-article-body"})
                            if find_abstract is not None:
                                find_abstract = find_abstract.find("div",{"class" : "c-article-section__content"})
                                find_abstract = find_abstract.find('p').getText()
                                abstract = find_abstract

print(scrap())