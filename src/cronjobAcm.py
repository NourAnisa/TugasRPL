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


"""
processScrappingAcm
mengambil data berdasarkan progress
"""
def newProcessScrappingAcm(init):
    try :
        conn = sqlite3.connect("./database.sqlite")
        data = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
        startPage = 0 
        limit = 0
        count_inst = 0
        if data is not None:
            startPage = data[4]
            limit = data[3]
            count_inst = data[2]

        scrapdata = conn.execute('SELECT * FROM scrapping_data where (sumber=?)',['acm']).fetchall()
        if len(scrapdata)>0:
            count_inst = len(scrapdata)

        if count_inst != limit :
            # https://dl.acm.org/action/doSearch?AllField=&expand=allstartPage%3D1&ContentItemType=research-article&ConceptID=118230&pageSize=50&startPage=1
            url = "https://dl.acm.org/action/doSearch?AllField=&expand=allstartPage%3D1&"
            params = {
                'ContentItemType' : 'research-article',
                'ConceptID': 118230,
                'pageSize' : 50,
                'startPage': startPage,
            }
            url = url + urllib.parse.urlencode(params)
            # print(url)
            
            source_page = requests.get(url, headers=headers, stream=True)
            if source_page.status_code == 200:
                # print('visit url success')
                html_source = source_page.content
                if html_source: 
                    # print('get source success')
                    source_page.close()
                    soup = BeautifulSoup(html_source, "html.parser")
                    getdata = soup.find_all("span", {"class": "hlFld-Title"})
                    if len(getdata)> 0:
                        counter = 0
                        for link in getdata:
                            # check stop or not
                            check_stop = conn.execute('select * from progress where (start_stop=? and id=?)',(1,init)).fetchone()
                            if check_stop is not None:
                                # print('not stop')
                                acm_link_master = link.find("a",href=True).get("href")
                                if acm_link_master is not None:
                                    nurl = "https://dl.acm.org"+acm_link_master
                                    # print('visit data '+str(nurl))
                                    check = conn.execute('SELECT * FROM scrapping_data WHERE (url=? AND sumber=?)', (nurl,'acm'))
                                    if check.fetchone() is None:
                                        opts = webdriver.FirefoxOptions()
                                        opts.headless = True

                                        browser_driver = webdriver.Firefox(options=opts)
                                        browser_driver.set_window_position(-1000000, 0)
                                        try:
                                            browser_driver.get(nurl)
                                            time.sleep(1)   
                                        except:
                                            browser_driver.quit()
                                            # browser_driver.get(nurl)
                                            # time.sleep(1)   
                                            # browser_driver.refresh()

                                        html_source_d = browser_driver.page_source
                                        soup_d = BeautifulSoup(html_source_d, "html.parser")
                                        browser_driver.quit()
                                        # browser_driver.quit()
                                        # print('get detail source success')

                                        title = soup_d.find("h1", {"class": "citation__title"})
                                        if title is not None : 
                                            title = title.getText()
                                        else: 
                                            title = ""

                                        authors = soup_d.find_all("li",{"class":"loa__item"})
                                        if len(authors)>0 :
                                            author = ""
                                            for auth in authors:
                                                authorval = auth.find("a",title=True).get("title")
                                                if len(author)> 0:
                                                    author = author +", "+ authorval
                                                else:
                                                    author = author + authorval
                                        else:
                                            author = ""

                                        tahun_terbit = soup_d.find("span",{"class" : "CitationCoverDate"})
                                        if tahun_terbit is not None :
                                            tahun_terbit = tahun_terbit.getText()
                                            # tahun_terbit = datetime.strptime(tahun_terbit, "%d %B %Y")
                                            # tahun_terbit = tahun_terbit.strftime("%Y-%m-%d")
                                        else:
                                            tahun_terbit = ""
                                        
                                        abstract = soup_d.find("div",{"class" : "abstractSection abstractInFull"})
                                        if abstract is not None:
                                            abstract = abstract.getText()
                                        else:
                                            abstract = ""
                                        
                                        check = conn.execute('select * from scrapping_data where (url=? and sumber=? and title=?)', (nurl,'acm',title))
                                        if check.fetchone() is None:
                                            print("The ACM Digital Library :  "+str(nurl))
                                            conn.execute("insert into scrapping_data (url, title, author, tahun_terbit, abstract, sumber) values (?, ?, ?, ?, ?, ?)", [nurl, title, author, tahun_terbit, abstract, 'acm'])
                                            conn.commit()
                                            # print("update record has been insert data....")
                                            # count = count_inst+1
                                            # conn.execute("UPDATE progress SET db_record=? WHERE id=?", [count, init])
                                            # conn.commit()
                                            getInsert = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
                                            if getInsert is not None:
                                                data__ = conn.execute('SELECT * FROM scrapping_data where (sumber=?)',['acm']).fetchall()
                                                count = len(data__)
                                                conn.execute("UPDATE progress SET db_record=? WHERE id=?", [count, init])
                                                conn.commit()

                                ## counter data 
                                counter = counter+1
                            else:
                                ## counter data 
                                counter = counter+0
                                # print('The ACM Digital Library : stop')
                                ## counter data 
                                # counter = counter+0

                        # change page
                        # print("check change page....")
                        if counter == len(getdata):
                            # print("change page....")
                            page_change = startPage +1
                            conn.execute("UPDATE progress SET last_page=? WHERE id=?", [page_change, init])
                            conn.commit()

        else:
            print("The ACM Digital Library :  Done")
            # delete_progress = conn.execute('SELECT * FROM progress where (id=?)',[init]).fetchone()
            # if delete_progress is not None:
            #     conn.execute("UPDATE progress SET last_page=? WHERE id=?", [0,, init])
            #     conn.commit()

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
    progress = conn.execute('select * from progress where (start_stop=? and sumber=?)',[1,'acm']).fetchone()
    # print('------ The ACM Digital Library -------')
    if progress is not None:
        print("The ACM Digital Library :  ...")
        newProcessScrappingAcm(progress[0])
        conn.close()
        time.sleep(2)
        runningJobs()
    else:
        time.sleep(2)
        runningJobs()