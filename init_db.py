import os,sys
import mysql.connector
import config
tables=["status_history","notifications","contact_requests","medicine_recommendations","urgent_needs","requests","inventory","donations","medicines","medicine_categories","pharmacies","ngo_profiles","users"]
def run(path,cur):
    text=open(path,encoding="utf-8").read()
    for stmt in text.split(";"):
        stmt=stmt.strip()
        if(stmt):
            cur.execute(stmt)
def wipe(cur):
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for t in tables:
        cur.execute(f"TRUNCATE TABLE {t}")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
def main():
    seed="--seed" in sys.argv
    reset="--reset" in sys.argv
    args={"host":config.dbhost,"port":config.dbport,"user":config.dbuser,"password":config.dbpass}
    if(config.dbca):
        args["ssl_ca"]=config.dbca
    conn=mysql.connector.connect(**args)
    cur=conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {config.dbname} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    conn.close()
    args["database"]=config.dbname
    conn=mysql.connector.connect(**args)
    cur=conn.cursor()
    here=os.path.dirname(os.path.abspath(__file__))
    run(os.path.join(here,"database","schema.sql"),cur)
    conn.commit()
    if(reset):
        wipe(cur)
        conn.commit()
        print("Existing data wiped.")
    if(seed):
        run(os.path.join(here,"database","sample.sql"),cur)
        conn.commit()
    cur.close()
    conn.close()
    print("Database ready"+(" with sample data" if seed else "")+".")
if(__name__=="__main__"):
    main()
