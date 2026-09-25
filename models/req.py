from db import query,txn,logsql,notesql
from util import logstat,daysleft
from models import notif,pharm,don
def create(bid,iid,qty,method,pid):
    if(method not in("direct","ngo","pharmacy")):
        raise ValueError("Invalid fetch method")
    item=query("SELECT city,quantity_available,expiry_date FROM inventory WHERE inventory_id=%s",(iid,),one=True)
    if(not item):
        raise ValueError("Inventory item not found")
    if(daysleft(item["expiry_date"])<0):
        raise ValueError("This medicine has expired")
    if(qty<1 or qty>item["quantity_available"]):
        raise ValueError("Quantity must be between 1 and the available stock")
    if(query("SELECT request_id FROM requests WHERE buyer_id=%s AND inventory_id=%s AND status='pending'",(bid,iid),one=True)):
        raise ValueError("You already have a pending request for this item")
    if(method=="pharmacy"):
        if(not pid or pharm.cityof(pid)!=item["city"]):
            raise ValueError("Select a pharmacy in the same city as the medicine")
    else:
        pid=None
    rid=query("INSERT INTO requests (buyer_id,inventory_id,quantity_requested,fetch_method,pharmacy_id) VALUES (%s,%s,%s,%s,%s)",(bid,iid,qty,method,pid),commit=True)
    logstat("request",rid,None,"pending",bid)
    return rid
def bybuyer(bid,city=None):
    return query("SELECT r.request_id,r.quantity_requested,r.fetch_method,r.status,r.created_at,m.medicine_name,i.city,n.name AS ngo_name,p.name AS pharmacy_name,p.phone AS pharmacy_phone,p.address AS pharmacy_address,s.name AS seller_name,s.phone AS seller_phone,c.contact_request_id AS contact FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users n ON i.ngo_id=n.user_id LEFT JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id LEFT JOIN contact_requests c ON c.buyer_id=r.buyer_id AND c.donation_id=i.donation_id AND c.status='approved' LEFT JOIN users s ON c.seller_id=s.user_id WHERE r.buyer_id=%s AND (%s IS NULL OR i.city=%s) ORDER BY r.created_at DESC,r.request_id DESC",(bid,city,city))
def byngo(ngoid):
    return query("SELECT r.*,m.medicine_name,i.city,i.condition_status,u.name AS buyer_name,u.phone AS buyer_phone,p.name AS pharmacy_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id LEFT JOIN pharmacies p ON r.pharmacy_id=p.pharmacy_id WHERE i.ngo_id=%s ORDER BY r.created_at DESC,r.request_id DESC",(ngoid,))
def byid(rid):
    return query("SELECT r.*,m.medicine_name,i.ngo_id,i.city,i.medicine_id,u.name AS buyer_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id JOIN users u ON r.buyer_id=u.user_id WHERE r.request_id=%s",(rid,),one=True)
def approve(rid,ngoid):
    def work(cur):
        cur.execute("SELECT r.buyer_id,r.inventory_id,r.quantity_requested,r.status,i.ngo_id,i.quantity_available FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE r.request_id=%s FOR UPDATE",(rid,))
        r=cur.fetchone()
        if(not r or r["ngo_id"]!=ngoid):
            raise ValueError("Request not found")
        if(r["status"]!="pending"):
            raise ValueError("Request is not pending")
        if(r["quantity_available"]<r["quantity_requested"]):
            raise ValueError("Not enough inventory")
        cur.execute("UPDATE inventory SET quantity_available=quantity_available-%s WHERE inventory_id=%s",(r["quantity_requested"],r["inventory_id"]))
        cur.execute("UPDATE requests SET status='approved' WHERE request_id=%s",(rid,))
        cur.execute(logsql,("request",rid,"pending","approved",ngoid))
        cur.execute(notesql,(r["buyer_id"],f"Your request #{rid} has been approved."))
    txn(work)
def move(rid,ngoid,old,new,msg):
    r=byid(rid)
    if(not r or r["ngo_id"]!=ngoid or r["status"]!=old):
        raise ValueError("Request not found or already handled")
    query("UPDATE requests SET status=%s WHERE request_id=%s AND status=%s",(new,rid,old),commit=True)
    logstat("request",rid,old,new,ngoid)
    if(msg):
        notif.add(r["buyer_id"],msg.format(rid=rid,med=r["medicine_name"]))
def reject(rid,ngoid):
    move(rid,ngoid,"pending","rejected","Your request #{rid} for {med} was rejected.")
def finish(rid,ngoid):
    move(rid,ngoid,"approved","completed",None)
def cancel(rid,bid):
    r=query("SELECT request_id FROM requests WHERE request_id=%s AND buyer_id=%s AND status='pending'",(rid,bid),one=True)
    if(not r):
        raise ValueError("Only your own pending requests can be cancelled")
    query("UPDATE requests SET status='rejected' WHERE request_id=%s AND status='pending'",(rid,),commit=True)
    logstat("request",rid,"pending","rejected",bid)
def buyerstats(bid,city=None):
    row=query("SELECT SUM(r.status IN ('pending','approved')) AS active,SUM(r.status='approved') AS approved,SUM(r.status='completed') AS completed FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE r.buyer_id=%s AND (%s IS NULL OR i.city=%s)",(bid,city,city),one=True)
    out={}
    for k in row:
        out[k]=int(row[k] or 0)
    return out
def ngostats(ngoid):
    a=query("SELECT COUNT(*) AS c FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE i.ngo_id=%s AND r.status='pending'",(ngoid,),one=True)["c"]
    b=query("SELECT COUNT(*) AS c FROM inventory WHERE ngo_id=%s",(ngoid,),one=True)["c"]
    return {"requests":a,"donations":don.count("pending"),"stock":b}
def count(status=None,city=None):
    return query("SELECT COUNT(*) AS c FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE (%s IS NULL OR r.status=%s) AND (%s IS NULL OR i.city=%s)",(status,status,city,city),one=True)["c"]
