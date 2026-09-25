from db import query,txn,logsql,notesql
from util import logstat
from models import notif
def create(sid,mid,qty,batch,exp,city,loc,cond):
    did=query("INSERT INTO donations (seller_id,medicine_id,quantity,batch_number,expiry_date,city,locality,condition_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(sid,mid,qty,batch,exp,city,loc,cond),commit=True)
    logstat("donation",did,None,"pending",sid)
    notif.add(sid,f"Your donation #{did} has been submitted and is pending NGO verification.")
    return did
def byid(did,city=None):
    return query("SELECT d.*,m.medicine_name,c.category_name,u.name AS seller_name FROM donations d JOIN medicines m ON d.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id JOIN users u ON d.seller_id=u.user_id WHERE d.donation_id=%s AND (%s IS NULL OR d.city=%s)",(did,city,city),one=True)
def bysel(sid,city=None):
    return query("SELECT d.*,m.medicine_name,c.category_name FROM donations d JOIN medicines m ON d.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id WHERE d.seller_id=%s AND (%s IS NULL OR d.city=%s) ORDER BY d.created_at DESC,d.donation_id DESC",(sid,city,city))
def pending(city=None):
    return query("SELECT d.*,m.medicine_name,c.category_name,u.name AS seller_name FROM donations d JOIN medicines m ON d.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id JOIN users u ON d.seller_id=u.user_id WHERE d.status='pending' AND (%s IS NULL OR d.city=%s) ORDER BY d.created_at,d.donation_id",(city,city))
def count(status=None,city=None):
    return query("SELECT COUNT(*) AS c FROM donations WHERE (%s IS NULL OR status=%s) AND (%s IS NULL OR city=%s)",(status,status,city,city),one=True)["c"]
def stats(sid,city=None):
    row=query("SELECT COUNT(*) AS total,SUM(status='pending') AS pending,SUM(status='verified') AS verified,SUM(status='rejected') AS rejected FROM donations WHERE seller_id=%s AND (%s IS NULL OR city=%s)",(sid,city,city),one=True)
    out={}
    for k in row:
        out[k]=int(row[k] or 0)
    return out
def verify(did,ngoid,medid=None):
    def work(cur):
        cur.execute("SELECT * FROM donations WHERE donation_id=%s FOR UPDATE",(did,))
        d=cur.fetchone()
        if(not d or d["status"]!="pending"):
            raise ValueError("Donation is not pending")
        cur.execute("SELECT medicine_name FROM medicines WHERE medicine_id=%s",(medid or d["medicine_id"],))
        m=cur.fetchone()
        if(not m):
            raise ValueError("Unknown medicine")
        d["medicine_id"]=medid or d["medicine_id"]
        cur.execute("UPDATE donations SET status='verified',ngo_id=%s,medicine_id=%s WHERE donation_id=%s",(ngoid,d["medicine_id"],did))
        cur.execute("INSERT INTO inventory (donation_id,medicine_id,quantity_available,expiry_date,city,locality,condition_status,ngo_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(did,d["medicine_id"],d["quantity"],d["expiry_date"],d["city"],d["locality"],d["condition_status"],ngoid))
        cur.execute(logsql,("donation",did,"pending","verified",ngoid))
        cur.execute(notesql,(d["seller_id"],f"Your donation #{did} of {m['medicine_name']} has been verified by an NGO and added to inventory."))
    txn(work)
def reject(did,reason,ngoid):
    def work(cur):
        cur.execute("SELECT seller_id,status FROM donations WHERE donation_id=%s FOR UPDATE",(did,))
        d=cur.fetchone()
        if(not d or d["status"]!="pending"):
            raise ValueError("Donation is not pending")
        cur.execute("UPDATE donations SET status='rejected',rejection_reason=%s,ngo_id=%s WHERE donation_id=%s",(reason,ngoid,did))
        cur.execute(logsql,("donation",did,"pending","rejected",ngoid))
        cur.execute(notesql,(d["seller_id"],f"Your donation #{did} was rejected. Reason: {reason}"))
    txn(work)
