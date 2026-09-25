from db import query
from models import notif,pharm
def create(rid,ngoid,medid,pid,reason):
    r=query("SELECT i.city,i.ngo_id,i.medicine_id,r.buyer_id FROM requests r JOIN inventory i ON r.inventory_id=i.inventory_id WHERE r.request_id=%s",(rid,),one=True)
    if(not r or r["ngo_id"]!=ngoid):
        raise ValueError("This request is not managed by your NGO")
    if(not query("SELECT medicine_id FROM medicines WHERE medicine_id=%s",(medid,),one=True)):
        raise ValueError("Unknown medicine")
    if(pharm.cityof(pid)!=r["city"]):
        raise ValueError("The pharmacy must be in the request city")
    recid=query("INSERT INTO medicine_recommendations (request_id,ngo_id,original_medicine_id,recommended_medicine_id,pharmacy_id,reason) VALUES (%s,%s,%s,%s,%s,%s)",(rid,ngoid,r["medicine_id"],medid,pid,reason),commit=True)
    notif.add(r["buyer_id"],f"An NGO has recommended an alternative medicine for your request #{rid}.")
    return recid
def bybuyer(bid,city=None):
    return query("SELECT mr.rec_id,mr.reason,mr.status,mr.created_at,m1.medicine_name AS original_name,m2.medicine_name AS recommended_name,p.name AS pharmacy_name,p.address AS pharmacy_address,n.name AS ngo_name FROM medicine_recommendations mr JOIN requests r ON mr.request_id=r.request_id JOIN inventory i ON r.inventory_id=i.inventory_id JOIN medicines m1 ON mr.original_medicine_id=m1.medicine_id JOIN medicines m2 ON mr.recommended_medicine_id=m2.medicine_id JOIN pharmacies p ON mr.pharmacy_id=p.pharmacy_id JOIN users n ON mr.ngo_id=n.user_id WHERE r.buyer_id=%s AND (%s IS NULL OR i.city=%s) ORDER BY mr.created_at DESC,mr.rec_id DESC",(bid,city,city))
def answer(recid,bid,action):
    status="accepted" if action=="accept" else "rejected"
    row=query("SELECT mr.ngo_id,mr.request_id FROM medicine_recommendations mr JOIN requests r ON mr.request_id=r.request_id WHERE mr.rec_id=%s AND r.buyer_id=%s AND mr.status='pending'",(recid,bid),one=True)
    if(not row):
        raise ValueError("Recommendation not found")
    query("UPDATE medicine_recommendations SET status=%s WHERE rec_id=%s",(status,recid),commit=True)
    notif.add(row["ngo_id"],f"Buyer has {status} your medicine recommendation for request #{row['request_id']}.")
