from functools import wraps
from datetime import datetime,date
import config

try:
    from flask import abort,request,session
    from flask_login import current_user
except ImportError:
    abort=request=session=current_user=None

try:
    from db import query,logsql
except ImportError:
    query=logsql=None
def fixcity(city):
    if not city:
        return None
    for c in config.cities:
        if c.lower()==str(city).strip().lower():
            return c
    return None
def free():
    return current_user.is_authenticated and current_user.role in("ngo","developer")
def getcity():
    city=fixcity(session.get("city"))
    if city:
        return city
    if current_user.is_authenticated:
        city=fixcity(current_user.city)
    return city or config.defcity
def setcity(city):
    city=fixcity(city) or config.defcity
    session["city"]=city
    return city
def scope():
    if free():
        return fixcity(request.args.get("city"))
    return getcity()
def needrole(*roles):
    def wrap(f):
        @wraps(f)
        def inner(*a,**k):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*a,**k)
        return inner
    return wrap
def toint(text):
    try:
        return int(str(text).strip())
    except (ValueError,TypeError):
        return 0
def logstat(kind,eid,old,new,by):
    query(logsql,(kind,eid,old,new,by),commit=True)
def tier(count):
    if count<3:
        return "New"
    if count<6:
        return "Bronze"
    if count<11:
        return "Silver"
    if count<21:
        return "Gold"
    return "Platinum"
def daysleft(d):
    if isinstance(d,str):
        try:
            d=datetime.strptime(d[:10],"%Y-%m-%d").date()
        except ValueError:
            return -1
    if isinstance(d,datetime):
        d=d.date()
    if not isinstance(d,date):
        return -1
    return (d-date.today()).days
def expclass(d):
    n=daysleft(d)
    if n>180:
        return "ok"
    if n>60:
        return "soon"
    return "critical"
def markexp(rows):
    out=[]
    for r in rows:
        nr=dict(r)
        nr["exp"]=expclass(nr.get("expiry_date"))
        out.append(nr)
    return out

def make_qr_svg(data):
    try:
        import qrcode
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgPathImage
        img = qrcode.make(str(data).strip(), image_factory=factory, border=2)
        return img.to_string().decode('utf-8')
    except Exception:
        clean = str(data)[:24]
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect width="160" height="160" fill="#f1f5f9" rx="8"/><text x="80" y="85" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#475569">QR: {clean}</text></svg>'
