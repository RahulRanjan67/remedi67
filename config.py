import os
envpath=os.path.join(os.path.dirname(os.path.abspath(__file__)),".env")
if(os.path.exists(envpath)):
    with open(envpath,encoding="utf-8-sig") as f:
        for line in f:
            line=line.strip()
            if(line and not line.startswith("#") and "=" in line):
                k,v=line.split("=",1)
                v=v.strip()
                if(len(v)>1 and v[0]==v[-1] and v[0] in "\"'"):
                    v=v[1:-1]
                os.environ.setdefault(k.strip(),v)
envcities=os.environ.get("REMEDI_CITIES") or os.environ.get("CITIES")
cities=[c.strip() for c in envcities.split(",") if c.strip()] if envcities else ["Demo City "+str(n) for n in range(1,11)]
defcity=os.environ.get("DEFAULT_CITY") or (cities[0] if cities else "Demo City 1")
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