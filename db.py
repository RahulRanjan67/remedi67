import mysql.connector
import config
logsql="INSERT INTO status_history (entity_type,entity_id,old_status,new_status,changed_by) VALUES (%s,%s,%s,%s,%s)"
notesql="INSERT INTO notifications (user_id,message) VALUES (%s,%s)"
def connect(usedb=True):
    args={"host":config.dbhost,"port":config.dbport,"user":config.dbuser,"password":config.dbpass,"autocommit":False}
    if(usedb):
        args["database"]=config.dbname
    if(config.dbca):
        args["ssl_ca"]=config.dbca
    return mysql.connector.connect(**args)
def opendb():
    try:
        return connect()
    except mysql.connector.Error as err:
        raise RuntimeError(f"Database connection error: {err}. Check the DB_* values in .env or the Vercel environment variables")
def query(sql,params=None,one=False,commit=False):
    conn=opendb()
    cur=conn.cursor(dictionary=True)
    try:
        cur.execute(sql,params or ())
        if(commit):
            conn.commit()
            return cur.lastrowid
        if(one):
            return cur.fetchone()
        return cur.fetchall()
    except mysql.connector.Error as err:
        conn.rollback()
        raise RuntimeError(f"Query error: {err}")
    finally:
        cur.close()
        conn.close()
def txn(work):
    conn=opendb()
    cur=conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        res=work(cur)
        conn.commit()
        return res
    except mysql.connector.Error as err:
        conn.rollback()
        raise RuntimeError(f"Transaction error: {err}")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
