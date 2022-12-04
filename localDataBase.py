import traceback
import asyncio
import sqlite3
from loguru import logger
import time

@logger.catch
def sqlLite2(nameDB:str, tabQuery:str):
    conn = sqlite3.connect(nameDB)
    cur = conn.cursor()
    try: 
        cur.execute(tabQuery)
    except:
        print('база уже создана')
    conn.commit()
    return conn


class SqlLite:
    
    @logger.catch
    def __init__(self, nameDB: str, tableQuery: str):
        self.nameDB = nameDB
        self.conn = sqlite3.connect(nameDB)
        self.cur  = self.conn.cursor()
        try:
            self.cur.execute(tableQuery)
            self.send_first() 
        except Exception as e :
            print('База данных уже создана [выполняеться подключение]')#, traceback.print_exc())
        self.conn.commit()

   
    #@asyncio.coroutine
    @logger.catch
    def send_first(self):
        print('Первая запись')
        self.cur.execute('insert into setting (string) values (1)')
        self.conn.commit()

    @logger.catch
    def update(self, variable: str, value: int):
        self.cur.execute(f"""update setting set {variable}="{value}" """)
        self.conn.commit()
  
    @logger.catch
    def get(self):
        """
            return: list - [0] номер последней строки
                           [1] последний id
        """
        query= 'select string, last_id, last_id_invoice from setting where id = 1'
        a = self.conn.execute(query)
        #print(list(a)[0])
        return list(a)[0]   
   
    def clear_column(self, nameTable):
        self.conn.execute(
        f"""
        DELETE FROM {nameTable} WHERE 1
        """)

print('создание таблицы')
sql = sqlLite2('temp.db', """create table questions(
        id integer primary key,
        id_user integer default 0,
        name text,
        command text,
        payload text);""")

