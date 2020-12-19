import sqlite3
import pandas as pd

# Simple SQLite class
class SimpleSQLite:

    def __init__(self, database):
        # the database property
        self.__database = database

    def executemany_sql(self, sql, params):
        # executemany interface with try/except/finally
        try:
            conn = sqlite3.connect(self.__database)
            conn.executemany(sql, params)
            conn.commit()
        except sqlite3.Error as error:
            print("Error while executing execute many", error)
        finally:
            if (conn):
                conn.close()

    def execute_sql(self, sql, msg=''):
        # execute / executescript interface with try/except/finally
        try:
            conn = sqlite3.connect(self.__database)
            if ';' in sql:
                conn.executescript(sql)
            else:
                cursor = conn.execute(sql)
                columns = cursor.description
                rows = cursor.fetchall()
                return rows, columns
            print(msg)
        except sqlite3.Error as error:
            print("Error while executing sql", error)
        finally:
            if (conn):
                conn.close()

    def pandas_dataframe(self, sql):
        # prepare the panda dataframe retrieving data from the database
        try:
            conn = sqlite3.connect(self.__database)
            return pd.read_sql_query(sql, conn)
        except:
            return None    
        finally:
            if (conn):
                conn.close()
                
