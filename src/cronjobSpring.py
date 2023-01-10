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
from src.Spring import Spring

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Accept-Encoding": "gzip, deflate",
#     "Connection": "keep-alive",
#     "Upgrade-Insecure-Requests": "1",
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Cache-Control": "max-age=0",
# }


"""
processScrappingIeee
mengambil data berdasarkan progress
"""
def newProcessScrappingSpring(init):
    try :
        conn = sqlite3.connect("./database.sqlite")
        totalPage = Spring().getTotalPageAndRecord(kategori="totalpage")
        start = 1

        data = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
        if data is not None:
            start = data[4]

        # print(start)

        for page in range(start,totalPage,1):
            url = "https://link.springer.com/search/page/"+str(page)+'?query=&facet-content-type="Article"'
            opts = webdriver.FirefoxOptions()
            opts.headless = True
            browser_driver = webdriver.Firefox(options=opts)
            browser_driver.set_window_position(-1000000, 0)
            try:
                browser_driver.get(url)
                time.sleep(1)   
            except:
                # browser_driver.get(url)
                # browser_driver.refresh()
                browser_driver.quit()

            html_source_d = browser_driver.page_source
            soup_d = BeautifulSoup(html_source_d, "html.parser")
            browser_driver.quit()
            if soup_d is not None:
                find_lists = soup_d.find("ol", {"id": "results-list"})
                if len(find_lists.find_all('li')) > 0:
                    counter = 0
                    find_lists = find_lists.find_all('li')
                    # print(len(find_lists))
                    for lists in find_lists:
                        # print(page)
                        check_stop = conn.execute('select * from progress where (start_stop=? and id=?)',(1,init)).fetchone()
                        if check_stop is not None:
                            link = lists.find('h2')
                            if link is not None:
                                link = link.find('a',href=True).get("href")
                                link = "https://link.springer.com"+link
                                # print(link)
                                # print(page)
                                ## visit link

                                check_url = conn.execute('select * from scrapping_data where (url=? and sumber=?)', (link,'spring')).fetchone()
                                if check_url is None:

                                    # print('found')
                                    opts_de = webdriver.FirefoxOptions()
                                    opts_de.headless = True
                                    browser_driver_de = webdriver.Firefox(options=opts_de)
                                    browser_driver_de.set_window_position(-1000000, 0)
                                    try:
                                        browser_driver_de.get(link)
                                        time.sleep(1)   
                                        # browser_driver_de.quit()
                                    except:
                                        browser_driver_de.quit()
                                        # browser_driver_de.get(link)
                                        # time.sleep(1)   
                                        # browser_driver_de.refresh()

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
                                            find_abstract = find_abstract.find_all('p')
                                            if len(find_abstract) > 0:
                                                find_abstract = find_abstract[0].getText()
                                                abstract = find_abstract
                                        

                                        if len(title)> 0 and len(authors)>0 and len(abstract)>0 and len(tahun_terbit)>0:
                                            check_title = conn.execute('select * from scrapping_data where (sumber=? and title=?)', ('spring',title))
                                            if check_title.fetchone() is None:
                                                print("Spinger Link :  "+str(url_))
                                                conn.execute("insert into scrapping_data (url, title, author, tahun_terbit, abstract, sumber) values (?, ?, ?, ?, ?, ?)", [url_, title, authors, tahun_terbit, abstract, 'spring'])
                                                conn.commit()
                                                # print("update record has been insert data....")

                                                getRecord = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
                                                if getRecord is not None:
                                                    data__ = conn.execute('SELECT * FROM scrapping_data where (sumber=?)',['spring']).fetchall()
                                                    count = len(data__)
                                                    conn.execute("UPDATE progress SET db_record=? WHERE id=?", [count, init])
                                                    conn.commit()

                            counter = counter+1
                    
                    if counter == len(find_lists):
                        getLas = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
                        if getLas is not None:
                            page_change = page
                            conn.execute("UPDATE progress SET last_page=? WHERE id=?", [page_change, init])
                            conn.commit()

    except requests.exceptions.ConnectionError as e:
        print('Error -> Connection :')
        print(e)
        pass

    except Exception:
        print('Error -> Coding :')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        pass

"""
=====================================
Start Prosess
=====================================
"""
def runningJobs():
    conn = sqlite3.connect("./database.sqlite")
    progress = conn.execute('select * from progress where (start_stop=? and sumber=?)',[1,'spring']).fetchone()
    if progress is not None:
        print("Spinger Link :  ...")
        newProcessScrappingSpring(progress[0])
        conn.close()
        time.sleep(2)
        runningJobs()
    else:
        time.sleep(2)
        runningJobs()