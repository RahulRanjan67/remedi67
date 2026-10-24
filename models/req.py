from db import query,txn,logsql,notesql
from util import logstat,daysleft,toint
from models import notif,pharm,don
def create(bid,iid,qty,method,pid):
    if method not in("direct","ngo","pharmacy"):
        raise ValueError("Invalid fetch method")
    item=query("SELECT city,quantity_available,expiry_date FROM inventory WHERE inventory_id=%s",(iid,),one=True)
    if not item:
        raise ValueError("Inventory item not found")
    if daysleft(item["expiry_date"])<0:
        raise ValueError("This medicine has expired")
    if qty<1 or qty>item["quantity_available"]:
        raise ValueError("Quantity must be between 1 and the available stock")
    if query("SELECT request_id FROM requests WHERE buyer_id=%s AND inventory_id=%s AND status='pending'",(bid,iid),one=True):
        raise ValueError("You already have a pending request for this item")
    if method=="pharmacy":
        pid=toint(pid)
        if not pid or pharm.cityof(pid)!=item["city"]:
            raise ValueError("Select a pharmacy in the same city as the medicine")
    else:
        pid=None
    rid=query("INSERT INTO requests (buyer_id,inventory_id,quantity_requested,fetch_method,pharmacy_id) VALUES (%s,%s,%s,%s,%s)",(bid,iid,qty,method,pid),commit=True)
    logstat("request",rid,None,"pending",bid)
    return rid
def bybuyer(bid,city=None):
    return query("SELECT r.request_id,r.quantity_requested,r.fetch_method,r.status,r.created_at,m.medicine_name,i.city,n.name AS ngo_name,p.name AS pharmacy_name,p.phone AS pharmacy_phone,p.address AS pharmacy_address,s.name AS seller_name,s.phone AS seller_phone,c.contact_request_id AS contact FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id LEFT JOIN users n ON i.ngo_id=n.user_id LEFT JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id LEFT JOIN contact_requests c ON c.buyer_id=r.buyer_id AND c.donation_id=i.donation_id AND c.status='approved' LEFT JOIN users s ON c.seller_id=s.user_id WHERE r.buyer_id=%s AND (%s IS NULL OR i.city=%s) ORDER BY r.created_at DESC,r.request_id DESC",(bid,city,city))
def byngo(ngoid):
    u=query("SELECT city FROM users WHERE user_id=%s",(ngoid,),one=True)
    ucity=u["city"] if u else None
    return query("SELECT r.*,m.medicine_name,i.city,i.condition_status,u.name AS buyer_name,u.phone AS buyer_phone,p.name AS pharmacy_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id LEFT JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id WHERE (i.ngo_id=%s OR (i.ngo_id IS NULL AND (%s IS NULL OR i.city=%s))) ORDER BY r.created_at DESC,r.request_id DESC",(ngoid,ucity,ucity))
def byid(rid):
    return query("SELECT r.*,m.medicine_name,i.ngo_id,i.city,i.medicine_id,u.name AS buyer_name,u.phone AS buyer_phone,u.email AS buyer_email,p.name AS pharmacy_name,p.address AS pharmacy_address FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id LEFT JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id WHERE r.request_id=%s",(rid,),one=True)
def bypharmacy(pid):
    return query("SELECT r.*,m.medicine_name,c.category_name,i.city,i.condition_status,i.expiry_date,d.batch_number,u.name AS buyer_name,u.phone AS buyer_phone,u.email AS buyer_email FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id JOIN donations d ON i.donation_id=d.donation_id JOIN users u ON r.buyer_id=u.user_id WHERE r.pharmacy_id=%s AND r.fetch_method='pharmacy' ORDER BY (r.status IN ('approved','ready')) DESC, r.created_at DESC",(pid,))
def pharmacy_stats(pid):
    row=query("SELECT COUNT(*) AS total,COALESCE(SUM(status='approved'),0) AS waiting,COALESCE(SUM(status='ready'),0) AS ready,COALESCE(SUM(status='completed'),0) AS dispensed FROM requests WHERE pharmacy_id=%s AND fetch_method='pharmacy'",(pid,),one=True)
    return {k:int(row[k] or 0) for k in row}
def ready_pharmacy(rid,pid,actor_uid):
    def work(cur):
        cur.execute("SELECT r.*,m.medicine_name,p.name AS pharmacy_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id WHERE r.request_id=%s AND r.pharmacy_id=%s FOR UPDATE",(rid,pid))
        r=cur.fetchone()
        if not r:
            raise ValueError("Request not found at this pharmacy")
        if r["status"]!="approved":
            raise ValueError("Request is not in approved state")
        cur.execute("UPDATE requests SET status='ready' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,"approved","ready",actor_uid))
        cur.execute(notesql,(r["buyer_id"],f"Your medicine {r['medicine_name']} (Request #{rid}) is packaged and ready for pickup at {r['pharmacy_name']}."))
    txn(work)
def dispense_pharmacy(rid,pid,actor_uid):
    def work(cur):
        cur.execute("SELECT r.*,m.medicine_name,p.name AS pharmacy_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id WHERE r.request_id=%s AND r.pharmacy_id=%s FOR UPDATE",(rid,pid))
        r=cur.fetchone()
        if not r:
            raise ValueError("Request not found at this pharmacy")
        if r["status"] not in("approved","ready"):
            raise ValueError("Request must be approved or ready before dispensing")
        cur.execute("UPDATE requests SET status='completed' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,r["status"],"completed",actor_uid))
        cur.execute(notesql,(r["buyer_id"],f"Your request #{rid} for {r['medicine_name']} has been dispensed by {r['pharmacy_name']}. Thank you!"))
    txn(work)
def approve(rid,ngoid):
    def work(cur):
        cur.execute("SELECT r.buyer_id,r.inventory_id,r.quantity_requested,r.status,i.ngo_id,i.quantity_available FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE r.request_id=%s FOR UPDATE",(rid,))
        r=cur.fetchone()
        if not r or (r["ngo_id"] and r["ngo_id"]!=ngoid):
            raise ValueError("Request not found")
        if r["status"]!="pending":
            raise ValueError("Request is not pending")
        if r["quantity_available"]<r["quantity_requested"]:
            raise ValueError("Not enough inventory")
        cur.execute("UPDATE inventory SET quantity_available=quantity_available-%s,ngo_id=COALESCE(ngo_id,%s) WHERE inventory_id=%s",(r["quantity_requested"],ngoid,r["inventory_id"]))
        cur.execute("UPDATE requests SET status='approved' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,"pending","approved",ngoid))
        cur.execute(notesql,(r["buyer_id"],f"Your request #{rid} has been approved."))
    txn(work)
def move(rid,ngoid,old,new,msg):
    def work(cur):
        cur.execute("SELECT r.*,m.medicine_name,i.ngo_id,u.name AS buyer_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id WHERE r.request_id=%s FOR UPDATE",(rid,))
        r=cur.fetchone()
        if not r or (r["ngo_id"] and r["ngo_id"]!=ngoid) or r["status"]!=old:
            raise ValueError("Request not found or already handled")
        cur.execute("UPDATE requests SET status=%s WHERE request_id=%s",(new,rid))
        cur.execute(logsql,("request",rid,old,new,ngoid))
        if msg:
            cur.execute(notesql,(r["buyer_id"],msg.format(rid=rid,med=r["medicine_name"])))
    txn(work)
def ready(rid,ngoid):
    move(rid,ngoid,"approved","ready","Your request #{rid} for {med} is ready for pickup.")
def finish(rid,ngoid):
    def work(cur):
        cur.execute("SELECT r.*,m.medicine_name,i.ngo_id,u.name AS buyer_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id WHERE r.request_id=%s FOR UPDATE",(rid,))
        r=cur.fetchone()
        if not r or (r["ngo_id"] and r["ngo_id"]!=ngoid) or r["status"] not in("approved","ready"):
            raise ValueError("Request not found or not ready to finish")
        cur.execute("UPDATE requests SET status='completed' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,r["status"],"completed",ngoid))
        cur.execute(notesql,(r["buyer_id"],f"Your request #{rid} for {r['medicine_name']} is completed."))
    txn(work)
def reject(rid,ngoid,reason="Your request was rejected."):
    def work(cur):
        cur.execute("SELECT r.*,m.medicine_name,i.ngo_id,u.name AS buyer_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id WHERE r.request_id=%s FOR UPDATE",(rid,))
        r=cur.fetchone()
        if not r or (r["ngo_id"] and r["ngo_id"]!=ngoid):
            raise ValueError("Request not found")
        if r["status"] not in("pending","approved","ready"):
            raise ValueError("Request cannot be rejected in current state")
        if r["status"] in("approved","ready"):
            cur.execute("UPDATE inventory SET quantity_available=quantity_available+%s WHERE inventory_id=%s",(r["quantity_requested"],r["inventory_id"]))
        cur.execute("UPDATE requests SET status='rejected' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,r["status"],"rejected",ngoid))
        cur.execute(notesql,(r["buyer_id"],f"Your request #{rid} for {r['medicine_name']} was rejected. {reason}"))
    txn(work)
def cancel(rid,bid):
    r=query("SELECT request_id FROM requests WHERE request_id=%s AND buyer_id=%s AND status='pending'",(rid,bid),one=True)
    if not r:
        raise ValueError("Only your own pending requests can be cancelled")
    query("UPDATE requests SET status='cancelled' WHERE request_id=%s AND status='pending'",(rid,),commit=True)
    logstat("request",rid,"pending","cancelled",bid)
def buyerstats(bid,city=None):
    row=query("SELECT SUM(r.status IN('pending','approved','ready')) AS active,SUM(r.status='approved') AS approved,SUM(r.status='ready') AS ready,SUM(r.status='completed') AS completed,SUM(r.status='cancelled') AS cancelled FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE r.buyer_id=%s AND (%s IS NULL OR i.city=%s)",(bid,city,city),one=True)
    out={}
    for k in row:
        out[k]=int(row[k] or 0)
    return out
def ngostats(ngoid):
    u=query("SELECT city FROM users WHERE user_id=%s",(ngoid,),one=True)
    ucity=u["city"] if u else None
    a=query("SELECT COUNT(*) AS c FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE (i.ngo_id=%s OR (i.ngo_id IS NULL AND (%s IS NULL OR i.city=%s))) AND r.status='pending'",(ngoid,ucity,ucity),one=True)["c"]
    b=query("SELECT COUNT(*) AS c FROM inventory WHERE (ngo_id=%s OR (ngo_id IS NULL AND (%s IS NULL OR city=%s)))",(ngoid,ucity,ucity),one=True)["c"]
    return {"requests":a,"donations":don.count("pending",ucity),"stock":b}
def count(status=None,city=None):
    return query("SELECT COUNT(*) AS c FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE (%s IS NULL OR r.status=%s) AND (%s IS NULL OR i.city=%s)",(status,status,city,city),one=True)["c"]
