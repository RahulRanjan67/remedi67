from db import query
base="SELECT i.*,m.medicine_name,c.category_name,u.name AS ngo_name,d.seller_id,su.name AS seller_name FROM inventory i JOIN medicines m ON i.medicine_id=m.medicine_id LEFT JOIN medicine_categories c ON m.category_id=c.category_id JOIN users u ON i.ngo_id=u.user_id JOIN donations d ON i.donation_id=d.donation_id JOIN users su ON d.seller_id=su.user_id "
def search(kw,cat,city,sort):
    sql=base+"WHERE i.quantity_available>0 AND i.expiry_date>=CURDATE() AND (%s IS NULL OR i.city=%s)"
    params=[city,city]
    if(kw):
        sql+=" AND m.medicine_name LIKE %s"
        params.append("%"+kw+"%")
    if(cat):
        sql+=" AND m.category_id=%s"
        params.append(cat)
    if(sort=="qty"):
        sql+=" ORDER BY i.quantity_available DESC"
    else:
        sql+=" ORDER BY i.expiry_date,i.inventory_id"
    return query(sql,params)
def byid(iid,city=None):
    return query(base+"WHERE i.inventory_id=%s AND (%s IS NULL OR i.city=%s)",(iid,city,city),one=True)
def byngo(ngoid,city=None,instock=False):
    sql="SELECT i.*,m.medicine_name FROM inventory i JOIN medicines m ON i.medicine_id=m.medicine_id WHERE i.ngo_id=%s AND (%s IS NULL OR i.city=%s)"
    if(instock):
        sql+=" AND i.quantity_available>0 AND i.expiry_date>=CURDATE()"
    return query(sql+" ORDER BY i.expiry_date,i.inventory_id",(ngoid,city,city))
def stats(city=None):
    row=query("SELECT COUNT(*) AS total,COALESCE(SUM(CASE WHEN quantity_available>0 AND expiry_date>=CURDATE() THEN quantity_available ELSE 0 END),0) AS avail FROM inventory WHERE (%s IS NULL OR city=%s)",(city,city),one=True)
    return {"total":int(row["total"]),"avail":int(row["avail"])}
