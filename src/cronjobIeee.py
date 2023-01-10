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
def newProcessScrappingIee(init):
    try :
        conn = sqlite3.connect("./database.sqlite")
        start = 0
        stop = 1000000000000

        data = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
        if data is not None:
            start = data[4]
        
        for i in range(start,stop,1):
            # check stop or not
            check_stop = conn.execute('select * from progress where (start_stop=? and id=?)',(1,init)).fetchone()
            if check_stop is not None:
                url_topic = "https://ieeexplore.ieee.org/document/"+str(i)

                opts = webdriver.FirefoxOptions()
                opts.headless = True

                browser_driver = webdriver.Firefox(options=opts)
                browser_driver.set_window_position(-1000000, 0)
                try:
                    browser_driver.get(url_topic)
                    time.sleep(1)   
                except:
                    # browser_driver.get(url_topic)
                    # browser_driver.refresh()
                    browser_driver.quit()

                html_source_d = browser_driver.page_source
                soup_d = BeautifulSoup(html_source_d, "html.parser")
                browser_driver.quit()
                exist = soup_d.find("div",{"class":"document-header-title-container col"})
                if exist is not None:
                    check_url = conn.execute('select * from scrapping_data where (url=? and sumber=?)', (url_topic,'ieee')).fetchone()
                    if check_url is None:
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
                            find_tahun = find_tahun.replace("Date of Publication: ","")
                            # find_tahun = datetime.strptime(find_tahun, "%d %B %Y")
                            # find_tahun = find_tahun.strftime("%Y-%m-%d")
                            # print(find_tahun)
                            tahun_terbit = find_tahun

                        abstract = ""
                        find_abstact = soup_d.find("div", {"class": "abstract-text row"})
                        if find_abstact is not None:
                            find_abstact = find_abstact.find_all("div", {"class": "u-mb-1"})
                            if len(find_abstact)>0:
                                abstract = find_abstact[0].find('div').getText()

                        # print(title,authors,abstract,tahun_terbit,sep="-||-")

                        if len(title)> 0 and len(authors)>0 and len(abstract)>0 and len(tahun_terbit)>0:
                            check_title = conn.execute('select * from scrapping_data where (sumber=? and title=?)', ('ieee',title))
                            if check_title.fetchone() is None:
                                print("IEEE Explore :  "+str(url_topic))
                                conn.execute("insert into scrapping_data (url, title, author, tahun_terbit, abstract, sumber) values (?, ?, ?, ?, ?, ?)", [url_topic, title, authors, tahun_terbit, abstract, 'ieee'])
                                conn.commit()
                                # print("update record has been insert data....")

                                getRecord = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
                                if getRecord is not None:
                                    data__ = conn.execute('SELECT * FROM scrapping_data where (sumber=?)',['ieee']).fetchall()
                                    count = len(data__)
                                    conn.execute("UPDATE progress SET db_record=? WHERE id=?", [count, init])
                                    conn.commit()
            
                getLas = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
                if getLas is not None:
                    count_last = i
                    conn.execute("UPDATE progress SET last_page=? WHERE id=?", [count_last, init])
                    conn.commit()
            # else:
                # print('IEEE Explore : stop')

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
    progress = conn.execute('select * from progress where (start_stop=? and sumber=?)',[1,'ieee']).fetchone()
    # print('------ The ACM Digital Library -------')
    if progress is not None:
        print("IEEE Explore :  ...")
        newProcessScrappingIee(progress[0])
        conn.close()
        time.sleep(2)
        runningJobs()
    else:
        time.sleep(2)
        runningJobs()