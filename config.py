import os
<<<<<<< HEAD
cities=["Demo City "+str(n) for n in range(1,11)]
defcity="Demo City 1"
=======
cities=["Bhopal","Ranchi","Delhi","Mumbai","Bengaluru","Hyderabad","Ahmedabad","Chennai","Kolkata","Pune"]
defcity="Bhopal"
>>>>>>> 5a99053c961840931d931a125222767de5151472
path=os.path.join(os.path.dirname(os.path.abspath(__file__)),".env")
if(os.path.exists(path)):
    with open(path,encoding="utf-8-sig") as f:
        for line in f:
            line=line.strip()
            if(line and not line.startswith("#") and "=" in line):
                key,val=line.split("=",1)
                val=val.strip()
                if(len(val)>1 and val[0]==val[-1] and val[0] in "\"'"):
                    val=val[1:-1]
                os.environ.setdefault(key.strip(),val)
dbhost=os.environ.get("DB_HOST","localhost")
dbport=int(os.environ.get("DB_PORT","3306"))
dbname=os.environ.get("DB_NAME","remedi")
dbuser=os.environ.get("DB_USER","root")
dbpass=os.environ.get("DB_PASSWORD","")
dbca=os.environ.get("DB_SSL_CA","")
SECRET_KEY=os.environ.get("SECRET_KEY","dev-secret")
MAX_CONTENT_LENGTH=16*1024*1024
onvercel=bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
SESSION_COOKIE_SAMESITE="Lax"
SESSION_COOKIE_SECURE=onvercel
if(onvercel and SECRET_KEY=="dev-secret"):
    raise RuntimeError("SECRET_KEY is not set in the Vercel project settings")
