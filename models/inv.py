from db import query
base="SELECT i.*,m.medicine_name,c.category_name,u.name AS ngo_name,d.seller_id,su.name AS seller_name,d.batch_number,d.status AS donation_status FROM inventory i JOIN medicines m ON i.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id LEFT JOIN users u ON i.ngo_id=u.user_id JOIN donations d ON i.donation_id=d.donation_id JOIN users su ON d.seller_id=su.user_id "
def search(kw,cat,city,sort):
    sql=base+"WHERE i.quantity_available>0 AND i.expiry_date>=CURDATE() AND (%s IS NULL OR i.city=%s)"
    params=[city,city]
    if kw:
        sql+=" AND m.medicine_name LIKE %s"
        params.append("%"+kw+"%")
    if cat:
        sql+=" AND m.category_id=%s"
        params.append(cat)
    if sort=="qty":
        sql+=" ORDER BY i.quantity_available DESC"
    else:
        sql+=" ORDER BY (i.ngo_id IS NOT NULL) DESC,i.expiry_date,i.inventory_id"
    return query(sql,params)
def byid(iid,city=None):
    return query(base+"WHERE i.inventory_id=%s AND (%s IS NULL OR i.city=%s)",(iid,city,city),one=True)
def byngo(ngoid,city=None,instock=False):
    sql="SELECT i.*,m.medicine_name FROM inventory i JOIN medicines m ON i.medicine_id=m.medicine_id WHERE i.ngo_id=%s AND (%s IS NULL OR i.city=%s)"
    if instock:
        sql+=" AND i.quantity_available>0 AND i.expiry_date>=CURDATE()"
    return query(sql+" ORDER BY i.expiry_date,i.inventory_id",(ngoid,city,city))
def stats(city=None):
    row=query("SELECT COUNT(*) AS total,COALESCE(SUM(CASE WHEN quantity_available>0 AND expiry_date>=CURDATE() THEN quantity_available ELSE 0 END),0) AS avail FROM inventory WHERE (%s IS NULL OR city=%s)",(city,city),one=True)
    return {"total":int(row["total"]),"avail":int(row["avail"])}
def needed(city=None):
    rows=query("SELECT DISTINCT medicine_id FROM urgent_needs WHERE status='open' AND (%s IS NULL OR city=%s)",(city,city))
    return {r["medicine_id"] for r in rows}
def quarantine_expired():
    rows=query("SELECT inventory_id,quantity_available FROM inventory WHERE expiry_date<CURDATE() AND quantity_available>0")
    if not rows:
        return 0
    iids=[r.get("inventory_id") for r in rows if r and r.get("inventory_id")]
    if not iids:
        return 0
    query("UPDATE inventory SET quantity_available=0 WHERE expiry_date<CURDATE() AND quantity_available>0",commit=True)
    for iid in iids:
        query("INSERT INTO status_history (entity_type,entity_id,old_status,new_status) VALUES (%s,%s,%s,%s)",("inventory",iid,"active","quarantined_expired"),commit=True)
        reqs=query("SELECT r.request_id,r.buyer_id,m.medicine_name FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m ON i.medicine_id=m.medicine_id WHERE r.inventory_id=%s AND r.status='pending'",(iid,))
        for rq in (reqs or []):
            if rq and rq.get("request_id"):
                query("UPDATE requests SET status='cancelled' WHERE request_id=%s",(rq["request_id"],),commit=True)
                query("INSERT INTO status_history (entity_type,entity_id,old_status,new_status) VALUES (%s,%s,%s,%s)",("request",rq["request_id"],"pending","cancelled"),commit=True)
                if rq.get("buyer_id"):
                    mname=rq.get("medicine_name") or "medication"
                    query("INSERT INTO notifications (user_id,message) VALUES (%s,%s)",(rq["buyer_id"],f"Your request #{rq['request_id']} for {mname} was cancelled because the medicine passed its expiration date."),commit=True)
    return len(iids)
