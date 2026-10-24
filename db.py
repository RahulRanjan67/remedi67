import mysql.connector
import mysql.connector.pooling
import config
logsql="INSERT INTO status_history (entity_type,entity_id,old_status,new_status,changed_by) VALUES (%s,%s,%s,%s,%s)"
notesql="INSERT INTO notifications (user_id,message) VALUES (%s,%s)"
_pool=None
def _getpool():
    global _pool
    if _pool is None:
        psize = 2 if config.onvercel else 5
        args={"pool_name":"remedi","pool_size":psize,"host":config.dbhost,"port":config.dbport,"user":config.dbuser,"password":config.dbpass,"database":config.dbname,"autocommit":False}
        if config.dbca:
            args["ssl_ca"]=config.dbca
        _pool=mysql.connector.pooling.MySQLConnectionPool(**args)
    return _pool
def connect(usedb=True):
    args={"host":config.dbhost,"port":config.dbport,"user":config.dbuser,"password":config.dbpass,"autocommit":False}
    if usedb:
        args["database"]=config.dbname
    if config.dbca:
        args["ssl_ca"]=config.dbca
    return mysql.connector.connect(**args)
def opendb():
    try:
        conn = _getpool().get_connection()
        try:
            if not conn.is_connected():
                conn.reconnect(attempts=2, delay=1)
            else:
                conn.ping(reconnect=True, attempts=2, delay=1)
        except Exception:
            pass
        return conn
    except mysql.connector.Error as err:
        try:
            return connect(usedb=True)
        except Exception as direct_err:
            raise RuntimeError(f"DB connection error: {err}. Direct fallback error: {direct_err}")
def query(sql,params=None,one=False,commit=False):
    conn=opendb()
    cur=conn.cursor(dictionary=True)
    try:
        cur.execute(sql,params or ())
        if commit:
            conn.commit()
            return cur.lastrowid
        return cur.fetchone() if one else cur.fetchall()
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
