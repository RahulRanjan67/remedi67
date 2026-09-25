from flask import Blueprint,render_template,redirect,url_for,flash
from flask_login import login_required
from db import query
from util import needrole,scope
from models import user,don,inv,req,urgent
bp=Blueprint("admin",__name__,url_prefix="/admin")
tables=["users","pharmacies","medicines","donations","inventory","requests","contact_requests","urgent_needs","medicine_recommendations","notifications"]
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
    return render_template("admin/dashboard.html",stats=stats,pending=user.pending(city),label=city or "all cities")
@bp.route("/users")
@login_required
@needrole("admin","developer")
def users():
    city=scope()
    return render_template("admin/users.html",users=user.everyone(city),label=city or "all cities")
@bp.route("/approve-ngo/<int:uid>",methods=["POST"])
@login_required
@needrole("admin","developer")
def approve(uid):
    user.approve(uid,scope())
    flash("NGO approved.","success")
    return redirect(url_for("admin.users"))
@bp.route("/developer/dashboard")
@login_required
@needrole("developer")
def devdash():
    counts={t:query("SELECT COUNT(*) AS c FROM "+t,one=True)["c"] for t in tables}
    return render_template("admin/dev_dashboard.html",counts=counts)
