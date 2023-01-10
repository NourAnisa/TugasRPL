from pipes import Template
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from src import Acm, Auth, cronjobAcm, Ieee, cronjobIeee, cronjobSpring, Spring, Clustering
import sqlite3
import math
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz


def runAcmJobs():
  print('running Acm jobs :')
  cronjobAcm.runningJobs()

def runIeeJobs():
  print('running Ieee jobs :')
  cronjobIeee.runningJobs()

def runSpringJobs():
  print('running Spring Link jobs :')
  cronjobSpring.runningJobs()

scheduler = BackgroundScheduler()
scheduler.add_job(func=runAcmJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='acm_job')
scheduler.add_job(func=runIeeJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='ieee_job')
scheduler.add_job(func=runSpringJobs, trigger="interval", days=1, next_run_time=datetime.now(pytz.timezone('Asia/Jakarta')), id='spring_job')
scheduler.start()

app = Flask(__name__,static_folder='assets',template_folder='templates')
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def home():
  title_page = "Welcome"
  return render_template("./pages/index.html", content={ "title_page" : title_page })

@app.route("/searching",methods=["GET"])
def dod_search():
  if request.method == "GET":
    
    # counter = 0
    limit = 20
    page = 1
    offset = 0

    same = 0
    listcluster = {
      1 : [],
      2 : [],
      3 : [],
      4 : [],
      5 : [],
    }
    listclustera = {
      1 : [],
      2 : [],
      3 : [],
      4 : [],
      5 : [],
    }

    conn = sqlite3.connect("./database.sqlite")
    keyword = request.args.get('keyword')
    clustercheck = conn.execute("select * FROM cluster_iteration where keyword=?",[keyword]).fetchall()
    if len(clustercheck)<=0:
      conn.execute("delete FROM cluster_iteration")
      conn.execute("delete FROM corpus")
      conn.commit()
      if len(keyword)> 0:
        Clustering(keyword=keyword).topicModel()
        Clustering(keyword=keyword).proses_clustering()
        

    reqpage = request.args.get('page')
    if reqpage is not None:
      page = int(reqpage)
      if int(page) > 1:
        offset = limit * (int(page)-1)

    lists = conn.execute("select * FROM scrapping_data where title like ?  or abstract like ?  ORDER BY title ASC LIMIT ?,?",["%"+keyword+"%","%"+keyword+"%",offset,limit]).fetchall()
    totalRecord = conn.execute("select * FROM scrapping_data where title like ?  or abstract like ?",["%"+keyword+"%","%"+keyword+"%"]).fetchall()
    totalRecord = len(totalRecord)

    showing = len(lists)

    clusteri = conn.execute("select * FROM cluster_iteration where keyword=? and type=?",[keyword,'1']).fetchall()
    if len(clusteri)>0:
      same = 1
    else:
      conn.execute("delete FROM cluster_iteration where keyword=? and type=?",[keyword,'1'])
      conn.execute("delete FROM corpus where keyword=? and type=?",[keyword,'1'])
      conn.commit()

    
    clustera = conn.execute("select * FROM cluster_iteration where keyword=? and type=?",[keyword,'2']).fetchall()
    if len(clustera)>0:
      same = 1
    else:
      conn.execute("delete FROM cluster_iteration where keyword=? and type=?",[keyword,'2'])
      conn.execute("delete FROM corpus where keyword=? and type=?",[keyword,'2'])
      conn.commit()
    
    
    if same == 1:
      for dt in clusteri:
        listcluster[dt[0]].append(dt[1])
      
      for dt in clustera:
        listclustera[dt[0]].append(dt[1])

    title_dis =  conn.execute("select * FROM corpus where keyword like ? and type=? LIMIT ?,?",["%"+keyword+"%","1",0,10]).fetchall()
    abstract_dis =  conn.execute("select * FROM corpus where keyword like ? and type=? LIMIT ?,?",["%"+keyword+"%","2",0,10]).fetchall()

    conn.close()
    title_page = "Search Jurnal or Article"

    return render_template("./pages/search.html", content={ "title_page" : title_page },keyword=keyword,lists=lists,totalRecord=totalRecord,showing=showing,page=page,limit=limit,same=same,listcluster=listcluster,listclustera=listclustera,title_dis=title_dis,abstract_dis=abstract_dis)

@app.route("/administrator/text-summer")
def administrator_text_summer():
  # if Auth('login').check() == True:
  data = ''
  init = request.args.get('init')
  data = Clustering(keyword='foo').text_summerize(init=init)
  return make_response(jsonify({
    'status' : True,
    'data' : data
  }), 200)
  # else:
  #   return make_response(jsonify({
  #     'status' : False,
  #   }), 200)

# @app.route("/search",methods=["POST"])
# def home_search():
#   if request.method == "POST":
#     keyword = request.form['search']
#     acm = Acm(keyword)
#   return acm.scrapping()
     
"""
  admin route
"""
@app.route("/administrator")
def administrator():
  if Auth('login').check() == True:
    return redirect(url_for('administrator_index'))
  else:
    title_page = "Login Page"
    return render_template("./pages/admin/login.html", content={ "title_page" : title_page })

@app.route("/process-login",methods=["POST"])
def process_login():
  if request.method == "POST":
    if request.form['username'] == 'admin' and request.form['password'] == 'admin':
      session['login'] = 'administrator'
      flash('Login Successfuly!')
      return redirect(url_for('administrator_index'))

  flash('Invalid credentials!')
  return redirect(url_for('administrator'))

@app.route("/administrator/dashboard")
def administrator_index():
  if Auth('login').check() == True:
    title_page = "Administrator page"
    return render_template("./pages/admin/index.html", content={ "title_page" : title_page})
  else:
    return redirect(url_for('administrator'))

@app.route("/administrator/load-total-records-chart")
def administrator_load_total_records_chart():
  if Auth('login').check() == True:
    acm = 0
    ieee = 0
    spring = 0
    
    conn = sqlite3.connect("./database.sqlite")
    get_acm = conn.execute("select * FROM scrapping_data where (sumber=?)",['acm']).fetchall()
    # if get_acm is not None:
    acm = len(get_acm)

    get_ieee = conn.execute("select * FROM scrapping_data where (sumber=?)",["ieee"]).fetchall()
    # if get_ieee is not None:
    ieee = len(get_ieee)

    get_spring = conn.execute("select * FROM scrapping_data where (sumber=?)",['spring']).fetchall()
    # if get_spring is not None:
    spring = len(get_spring)

    conn.commit()
    conn.close()

    return make_response(jsonify({
      'status' : True,
      'data' : {
        'acm' : acm,
        'ieee' : ieee,
        'spring' : spring,
      }
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False,
    }), 200)

@app.route("/administrator/scrapping")
def administrator_scrapping():
  if Auth('login').check() == True:
    title_page = "Administrator page"

    ## insert to database if not exist
    Acm().insertPass()
    Ieee().insertPass()
    Spring().insertPass()

    conn = sqlite3.connect("./database.sqlite")
    progress_db = conn.execute("select * FROM progress").fetchall()

    return render_template("./pages/admin/scrapping.html", content={ "title_page" : title_page},progress_db=progress_db)
  else:
    return redirect(url_for('administrator'))

# @app.route("/administrator/scrapping/get-record",methods=["POST"])
# def administrator_scrapping_get_record():
#   if Auth('login').check() == True:

#     if request.method == "POST":
#       keyword = request.form['search']
      
#       if len(keyword)>0:
#         conn = sqlite3.connect("./database.sqlite")

#         for x in range(1):
#           _type = ''
#           if x == 0:
#             _type = 'acm'
#             allrecord = Acm().getRecord()
#           elif x == 1:
#             _type = 'ieee'
#           elif x == 2:
#             _type = 'springer link'
#           else:
#             _type = 'google scholar'

#           conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page) values (?, ?, ?, ?, ?)", [_type, 0, allrecord, 0])
#           conn.commit()

#       return redirect(url_for('administrator_scrapping'))
#   else:
#     return redirect(url_for('administrator'))
    
@app.route("/administrator/scrapping/get-total-db",methods=["GET"])
def administrator_scrapping_get_total_db():
  if Auth('login').check() == True:
    conn = sqlite3.connect("./database.sqlite")
    limit = 0
    hasinsert = 0
    break_ = False
    percent = 0

    init = request.args.get('init')
    init = int(init)

    check_0 = conn.execute("select * from progress where (id=?)",[init]).fetchone()
    if check_0 is not None:
      limit = check_0[3]
      check_1 = conn.execute("select * from scrapping_data where (sumber=?)",[check_0[1]]).fetchall()
      hasinsert = len(check_1)
      if check_0[5] == 0:
        break_ = True
      else:
        break_ = False


    percent = 0
    if check_0[1] == 'acm':
      if hasinsert >0 and limit >0 :
        percent = math.ceil(((hasinsert/int(limit))*100))

    if check_0[1] == 'spring':
      if hasinsert >0 and limit >0 :
        percent = math.ceil(((hasinsert/int(limit))*100))

    return make_response(jsonify({
      'status' : True,
      'data' : {
        'percent' : percent,
        'break' : break_,
        'limit': limit,
        'hasinsert':hasinsert
      }
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False,
    }), 200)


@app.route("/administrator/start-stop",methods=["GET"])
def administrator_scrapping_start_top():
  if Auth('login').check() == True:
    conn = sqlite3.connect("./database.sqlite")

    init = request.args.get('init')
    init = int(init)
    value = request.args.get('value')
    value = int(value)

    check = conn.execute("select * from progress where (id=?)",[init]).fetchone()
    if check is not None:
      if value == 0:
        if check[1] == 'acm':
          Acm().updateRecord()

        if check[1] == 'spring':
          Spring().updateRecord()

      if value == 0:
        val = 1
      else:
        val = 0
      conn.execute("UPDATE progress SET start_stop=? WHERE id=?", [val, init])
      conn.commit()

    return make_response(jsonify({
      'status' : True
    }), 200)
  else:
    return make_response(jsonify({
      'status' : False
    }), 200)

@app.route("/administrator/data")
def administrator_data():
  if Auth('login').check() == True:
    
    title_page = "Administrator page"
    conn = sqlite3.connect("./database.sqlite")
    # data = conn.execute("SELECT * FROM scrapping_data Limit ?, ?",('0','10')).fetchall()
    data = conn.execute("SELECT * FROM scrapping_data").fetchall()

    return render_template("./pages/admin/data.html", content={ "title_page" : title_page}, data = data)
  else:
    return redirect(url_for('administrator'))


@app.route('/logout')
def logout():
  # remove the username from the session if it is there
  session.pop('login', None)
  flash('Logout Successfuly!')
  return redirect(url_for('administrator'))

if __name__ == '__main__':
  app.run(debug=False)