from db import query
def bycity(city=None):
    return query("SELECT * FROM pharmacies WHERE is_active=1 AND (%s IS NULL OR city=%s) ORDER BY city,name",(city,city))
def bypin(pin,city=None):
    return query("SELECT * FROM pharmacies WHERE is_active=1 AND pincode=%s AND (%s IS NULL OR city=%s) ORDER BY city,name",(pin,city,city))
def cityof(pid):
    row=query("SELECT city FROM pharmacies WHERE pharmacy_id=%s AND is_active=1",(pid,),one=True)
    return row["city"] if row else None
def create(name,address,city,pin,phone):
    return query("INSERT INTO pharmacies (name,address,city,pincode,phone,is_active) VALUES (%s,%s,%s,%s,%s,1)",(name,address,city,pin,phone),commit=True)
