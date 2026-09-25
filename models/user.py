from db import query
from util import tier
class account:
    def __init__(self,data):
        self.__dict__.update(data)
        self.is_authenticated=True
        self.is_active=bool(data.get("is_approved",1))
        self.is_anonymous=False
    def get_id(self):
        return str(self.user_id)
def byid(uid):
    return query("SELECT * FROM users WHERE user_id=%s",(uid,),one=True)
def byemail(email):
    return query("SELECT * FROM users WHERE email=%s",(email,),one=True)
def create(name,email,pwhash,role,phone,city,pin,loc):
    ok=0 if role=="ngo" else 1
    return query("INSERT INTO users (name,email,password_hash,role,phone,city,pincode,locality,is_approved) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,email,pwhash,role,phone,city,pin,loc,ok),commit=True)
def approve(uid,city=None):
    query("UPDATE users SET is_approved=1 WHERE user_id=%s AND role='ngo' AND (%s IS NULL OR city=%s)",(uid,city,city),commit=True)
def pending(city=None):
    return query("SELECT * FROM users WHERE role='ngo' AND is_approved=0 AND (%s IS NULL OR city=%s) ORDER BY user_id",(city,city))
def everyone(city=None):
    return query("SELECT * FROM users WHERE (%s IS NULL OR city=%s) ORDER BY user_id",(city,city))
def stats(city=None):
    row=query("SELECT COUNT(*) AS total,SUM(role='seller') AS sellers,SUM(role='buyer') AS buyers,SUM(role='ngo') AS ngos,SUM(role='ngo' AND is_approved=0) AS pending FROM users WHERE (%s IS NULL OR city=%s)",(city,city),one=True)
    out={}
    for k in row:
        out[k]=int(row[k] or 0)
    return out
def donor(sid):
    row=query("SELECT COUNT(*) AS c FROM donations WHERE seller_id=%s AND status='verified'",(sid,),one=True)
    return tier(row["c"]),row["c"]
def update(uid,name,phone,city,pin,loc):
    query("UPDATE users SET name=%s,phone=%s,city=%s,pincode=%s,locality=%s WHERE user_id=%s",(name,phone,city,pin,loc,uid),commit=True)
