import time
from db import query
lastref={}
def create(bid,mid,qty,city,loc):
    if qty<1:
        raise ValueError("Quantity must be at least 1")
    if query("SELECT urgent_id FROM urgent_needs WHERE buyer_id=%s AND medicine_id=%s AND city=%s AND status='open'",(bid,mid,city),one=True):
        raise ValueError("Open urgent need already exists for this medicine in this city")
    return query("INSERT INTO urgent_needs (buyer_id,medicine_id,quantity_required,city,locality) VALUES (%s,%s,%s,%s,%s)",(bid,mid,qty,city,loc),commit=True)
def live(city=None):
    return query("SELECT un.*,m.medicine_name,u.name AS buyer_name FROM urgent_needs un JOIN medicines m ON un.medicine_id=m.medicine_id JOIN users u ON un.buyer_id=u.user_id WHERE un.status='open' AND (%s IS NULL OR un.city=%s) ORDER BY un.created_at DESC,un.urgent_id DESC",(city,city))
def bybuyer(bid,city=None):
    return query("SELECT un.*,m.medicine_name FROM urgent_needs un JOIN medicines m ON un.medicine_id=m.medicine_id WHERE un.buyer_id=%s AND (%s IS NULL OR un.city=%s) ORDER BY un.created_at DESC,un.urgent_id DESC",(bid,city,city))
def count(status=None,city=None):
    return query("SELECT COUNT(*) AS c FROM urgent_needs WHERE (%s IS NULL OR status=%s) AND (%s IS NULL OR city=%s)",(status,status,city,city),one=True)["c"]
def refresh(city=None):
    k=city or "all"
    if time.time()-lastref.get(k,0)<60:
        return
    lastref[k]=time.time()
    matches=query(
        "SELECT un.urgent_id,un.buyer_id,m.medicine_name,un.city,SUM(i.quantity_available) AS avail "
        "FROM urgent_needs un "
        "JOIN medicines m ON un.medicine_id=m.medicine_id "
        "JOIN inventory i ON i.medicine_id=un.medicine_id AND i.city=un.city AND i.quantity_available>0 AND i.expiry_date>=CURDATE() "
        "WHERE un.status='open' AND (%s IS NULL OR un.city=%s) "
        "GROUP BY un.urgent_id,un.buyer_id,m.medicine_name,un.city,un.quantity_required "
        "HAVING avail>=un.quantity_required",
        (city,city)
    )
    for m in (matches or []):
        notif_prefix=f"Urgent Need In Stock: {m['medicine_name']}"
        existing=query(
            "SELECT notification_id FROM notifications WHERE user_id=%s AND message LIKE %s",
            (m["buyer_id"], f"%{notif_prefix}%"),
            one=True
        )
        if not existing:
            query(
                "INSERT INTO notifications (user_id,message) VALUES (%s,%s)",
                (m["buyer_id"], f"{notif_prefix} is now available in {m['city']}. Check inventory to submit a request."),
                commit=True
            )
def fulfill(urgent_id,buyer_id):
    query("UPDATE urgent_needs SET status='fulfilled' WHERE urgent_id=%s AND buyer_id=%s",(urgent_id,buyer_id),commit=True)
