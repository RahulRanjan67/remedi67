import time
from flask import Blueprint,render_template,redirect,url_for,flash,session
from flask_login import login_required
from db import query
from util import needrole,scope
import config
from models import user,don,inv,req,urgent
bp=Blueprint("admin",__name__,url_prefix="/admin")
tables=["users","pharmacies","medicines","donations","inventory","requests","contact_requests","urgent_needs","medicine_recommendations","notifications","status_history"]
@bp.route("/dashboard")
@login_required
@needrole("admin","developer")
def dash():
    city=scope()
    stats=user.stats(city)
    stats["donations"]=don.count(None,city)
    stats["verified"]=don.count("verified",city)
    stats["waiting"]=don.count("pending",city)
    stats["stock"]=inv.stats(city)["total"]
    stats["requests"]=req.count("pending",city)
    stats["needs"]=urgent.count("open",city)
    stats["pharms"]=query("SELECT COUNT(*) AS c FROM pharmacies WHERE is_active=1 AND (%s IS NULL OR city=%s)",(city,city),one=True)["c"]
    audits=query("SELECT h.*,u.name AS actor FROM status_history h LEFT JOIN users u ON h.changed_by=u.user_id ORDER BY h.changed_at DESC,h.history_id DESC LIMIT 10")
    cityrows=query("SELECT d.city,COUNT(DISTINCT d.donation_id) AS dons,COUNT(DISTINCT CASE WHEN d.status='verified' THEN d.donation_id END) AS ver,COUNT(DISTINCT CASE WHEN d.status='rejected' THEN d.donation_id END) AS rej,COUNT(DISTINCT i.inventory_id) AS invs FROM donations d LEFT JOIN inventory i ON i.city=d.city GROUP BY d.city ORDER BY d.city")
    return render_template("admin/dashboard.html",stats=stats,pending=user.pending(city),label=city or "all cities",audits=audits,cityrows=cityrows)
@bp.route("/users")
@login_required
@needrole("admin","developer")
def users():
    city=scope()
    return render_template("admin/users.html",users=user.everyone(city),label=city or "all cities")
@bp.route("/audit-log")
@login_required
@needrole("admin","developer")
def auditlog():
    logs=query("SELECT h.*,u.name AS actor FROM status_history h LEFT JOIN users u ON h.changed_by=u.user_id ORDER BY h.changed_at DESC,h.history_id DESC LIMIT 100")
    return render_template("admin/audit_log.html",logs=logs)
@bp.route("/approve-ngo/<int:uid>",methods=["POST"])
@login_required
@needrole("admin","developer")
def approve(uid):
    user.approve(uid,scope())
    flash("NGO approved successfully.","success")
    return redirect(url_for("admin.users"))
@bp.route("/developer/dashboard")
@login_required
@needrole("developer")
def devdash():
    counts={t:query("SELECT COUNT(*) AS c FROM "+t,one=True)["c"] for t in tables}
    recent=query("SELECT h.*,u.name AS actor FROM status_history h LEFT JOIN users u ON h.changed_by=u.user_id ORDER BY h.changed_at DESC,h.history_id DESC LIMIT 25")
    psize=2 if config.onvercel else 5
    dbinfo={"host":config.dbhost,"port":config.dbport,"name":config.dbname,"user":config.dbuser,"poolsize":psize,"ssl":bool(config.dbca),"vercel":config.onvercel}
    return render_template("admin/dev_dashboard.html",counts=counts,recent=recent,dbinfo=dbinfo)
@bp.route("/developer/ping-db",methods=["POST"])
@login_required
@needrole("developer")
def devping():
    t0=time.time()
    query("SELECT 1",one=True)
    ms=round((time.time()-t0)*1000,2)
    flash(f"Database ping test ok: {ms}ms latency","success")
    return redirect(url_for("admin.devdash"))
@bp.route("/developer/trigger-refresh",methods=["POST"])
@login_required
@needrole("developer")
def devrefresh():
    urgent.refresh(None)
    flash("Triggered urgent needs inventory check","info")
    return redirect(url_for("admin.devdash"))
@bp.route("/developer/clear-cache",methods=["POST"])
@login_required
@needrole("developer")
def devclear():
    session.pop("unread",None)
    session.pop("unread_ts",None)
    flash("Flushed session notification cache","info")
    return redirect(url_for("admin.devdash"))
