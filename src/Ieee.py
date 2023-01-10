import sqlite3

class Ieee:
    def __init__(self):
        self

    def insertPass(self):
        conn = sqlite3.connect("./database.sqlite")
        slc = conn.execute('select * from progress where (sumber=?)',['ieee']).fetchone()

        if slc is None:
            record = 1000000000000
            conn.execute("insert into progress (sumber, db_record, scrapping_record, last_page, start_stop) values (?, ?, ?, ?, ?)",['ieee',0,record,0,0])
            conn.commit()