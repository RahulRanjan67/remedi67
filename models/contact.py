from db import query
from models import notif
def create(bid,sid,did):
    if query("SELECT contact_request_id FROM contact_requests WHERE buyer_id=%s AND donation_id=%s",(bid,did),one=True):
        raise ValueError("Contact request already sent")
    cid=query("INSERT INTO contact_requests (buyer_id,seller_id,donation_id) VALUES (%s,%s,%s)",(bid,sid,did),commit=True)
    notif.add(sid,"You have a new contact request.")
    return cid
def bybuyer(bid,city=None):
    return query("SELECT cr.contact_request_id,cr.status,cr.requested_at,cr.donation_id,m.medicine_name,d.city,d.locality,CASE WHEN cr.status='approved' THEN u.name END AS seller_name,CASE WHEN cr.status='approved' THEN u.phone END AS seller_phone,CASE WHEN cr.status='approved' THEN u.email END AS seller_email FROM contact_requests cr JOIN donations d ON cr.donation_id=d.donation_id JOIN medicines m ON d.medicine_id=m.medicine_id JOIN users u ON cr.seller_id=u.user_id WHERE cr.buyer_id=%s AND (%s IS NULL OR d.city=%s) ORDER BY cr.requested_at DESC,cr.contact_request_id DESC",(bid,city,city))
def byseller(sid,city=None):
    return query("SELECT cr.contact_request_id,cr.status,cr.requested_at,cr.donation_id,m.medicine_name,d.city,d.locality,u.name AS buyer_name,u.phone AS buyer_phone,u.email AS buyer_email FROM contact_requests cr JOIN users u ON cr.buyer_id=u.user_id JOIN donations d ON cr.donation_id=d.donation_id JOIN medicines m ON d.medicine_id=m.medicine_id WHERE cr.seller_id=%s AND (%s IS NULL OR d.city=%s) ORDER BY cr.requested_at DESC,cr.contact_request_id DESC",(sid,city,city))
def mapbybuyer(bid):
    rows=query("SELECT donation_id,status FROM contact_requests WHERE buyer_id=%s",(bid,))
    return {r["donation_id"]:r["status"] for r in rows}
def reply(cid,sid,action):
    status="approved" if action=="approve" else "rejected"
    row=query("SELECT buyer_id FROM contact_requests WHERE contact_request_id=%s AND seller_id=%s AND status='pending'",(cid,sid),one=True)
    if not row:
        raise ValueError("Contact request not found")
    query("UPDATE contact_requests SET status=%s,responded_at=CURRENT_TIMESTAMP WHERE contact_request_id=%s",(status,cid),commit=True)
    notif.add(row["buyer_id"],f"Your contact request has been {status}.")
