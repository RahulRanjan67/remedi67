from db import query
def create(bid,mid,qty,city,loc):
    return query("INSERT INTO urgent_needs (buyer_id,medicine_id,quantity_required,city,locality) VALUES (%s,%s,%s,%s,%s)",(bid,mid,qty,city,loc),commit=True)
def live(city=None):
    return query("SELECT un.*,m.medicine_name,u.name AS buyer_name FROM urgent_needs un JOIN medicines m ON un.medicine_id=m.medicine_id JOIN users u ON un.buyer_id=u.user_id WHERE un.status='open' AND (%s IS NULL OR un.city=%s) ORDER BY un.created_at DESC,un.urgent_id DESC",(city,city))
def bybuyer(bid,city=None):
    return query("SELECT un.*,m.medicine_name FROM urgent_needs un JOIN medicines m ON un.medicine_id=m.medicine_id WHERE un.buyer_id=%s AND (%s IS NULL OR un.city=%s) ORDER BY un.created_at DESC,un.urgent_id DESC",(bid,city,city))
def count(status=None,city=None):
    return query("SELECT COUNT(*) AS c FROM urgent_needs WHERE (%s IS NULL OR status=%s) AND (%s IS NULL OR city=%s)",(status,status,city,city),one=True)["c"]
def refresh(city=None):
    query("UPDATE urgent_needs SET status='fulfilled' WHERE status='open' AND (%s IS NULL OR city=%s) AND quantity_required<=(SELECT COALESCE(SUM(i.quantity_available),0) FROM inventory i WHERE i.medicine_id=urgent_needs.medicine_id AND i.city=urgent_needs.city AND i.quantity_available>0 AND i.expiry_date>=CURDATE())",(city,city),commit=True)
