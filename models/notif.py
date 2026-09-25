from db import query,notesql
def add(uid,msg):
    return query(notesql,(uid,msg),commit=True)
def mine(uid,limit=50):
    return query("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC,notification_id DESC LIMIT %s",(uid,limit))
def markall(uid):
    query("UPDATE notifications SET is_read=1 WHERE user_id=%s",(uid,),commit=True)
def unread(uid):
    return query("SELECT COUNT(*) AS c FROM notifications WHERE user_id=%s AND is_read=0",(uid,),one=True)["c"]
