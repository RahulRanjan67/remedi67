from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from util import needrole,scope,markexp,toint
from models import don,req,inv,rec,pharm,med
bp=Blueprint("ngo",__name__,url_prefix="/ngo")
@bp.route("/dashboard")
@login_required
@needrole("ngo")
def dash():
    return render_template("ngo/dashboard.html",stats=req.ngostats(current_user.user_id))
@bp.route("/verify-donations")
@login_required
@needrole("ngo")
def verify():
    city=scope()
    return render_template("ngo/verify_donations.html",donations=markexp(don.pending(city)),medicines=med.every(),sel=city)
@bp.route("/donations/<int:did>/verify",methods=["POST"])
@login_required
@needrole("ngo")
def accept(did):
    try:
        don.verify(did,current_user.user_id,toint(request.form.get("corrected_medicine_id")) or None)
        flash(f"Donation {did} verified and added to inventory.","success")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("ngo.verify"))
@bp.route("/donations/<int:did>/reject",methods=["POST"])
@login_required
@needrole("ngo")
def decline(did):
    try:
        don.reject(did,request.form.get("reason","").strip() or "Rejected by NGO",current_user.user_id)
        flash(f"Donation {did} rejected.","info")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("ngo.verify"))
@bp.route("/donations/bulk-verify",methods=["POST"])
@login_required
@needrole("ngo")
def bulkverify():
    done=0
    for did in request.form.getlist("donation_ids"):
        try:
            don.verify(toint(did),current_user.user_id)
            done+=1
        except ValueError:
            pass
    flash(f"{done} donations verified.","success")
    return redirect(url_for("ngo.verify"))
@bp.route("/donations/bulk-reject",methods=["POST"])
@login_required
@needrole("ngo")
def bulkdecline():
    reason=request.form.get("reason","").strip() or "Rejected by NGO"
    done=0
    for did in request.form.getlist("donation_ids"):
        try:
            don.reject(toint(did),reason,current_user.user_id)
            done+=1
        except ValueError:
            pass
    flash(f"{done} donations rejected.","info")
    return redirect(url_for("ngo.verify"))
@bp.route("/manage-requests")
@login_required
@needrole("ngo")
def manage():
    return render_template("ngo/manage_requests.html",requests=req.byngo(current_user.user_id))
@bp.route("/requests/<int:rid>/approve",methods=["POST"])
@login_required
@needrole("ngo")
def approve(rid):
    try:
        req.approve(rid,current_user.user_id)
        flash("Request approved.","success")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("ngo.manage"))
@bp.route("/requests/<int:rid>/reject",methods=["POST"])
@login_required
@needrole("ngo")
def deny(rid):
    try:
        req.reject(rid,current_user.user_id)
        flash("Request rejected.","info")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("ngo.manage"))
@bp.route("/requests/<int:rid>/complete",methods=["POST"])
@login_required
@needrole("ngo")
def finish(rid):
    try:
        req.finish(rid,current_user.user_id)
        flash("Request marked as completed.","success")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("ngo.manage"))
@bp.route("/requests/bulk-approve",methods=["POST"])
@login_required
@needrole("ngo")
def bulkapprove():
    done=0
    for rid in request.form.getlist("request_ids"):
        try:
            req.approve(toint(rid),current_user.user_id)
            done+=1
        except ValueError:
            pass
    flash(f"{done} requests approved.","success")
    return redirect(url_for("ngo.manage"))
@bp.route("/requests/bulk-reject",methods=["POST"])
@login_required
@needrole("ngo")
def bulkdeny():
    done=0
    for rid in request.form.getlist("request_ids"):
        try:
            req.reject(toint(rid),current_user.user_id)
            done+=1
        except ValueError:
            pass
    flash(f"{done} requests rejected.","info")
    return redirect(url_for("ngo.manage"))
@bp.route("/inventory")
@login_required
@needrole("ngo")
def stock():
    return render_template("ngo/inventory.html",inventory=markexp(inv.byngo(current_user.user_id,scope())))
@bp.route("/recommend/<int:rid>",methods=["GET","POST"])
@login_required
@needrole("ngo")
def suggest(rid):
    r=req.byid(rid)
    if(not r or r["ngo_id"]!=current_user.user_id):
        flash("Request not found.","danger")
        return redirect(url_for("ngo.manage"))
    if(request.method=="POST"):
        try:
            rec.create(rid,current_user.user_id,toint(request.form.get("recommended_medicine_id")),request.form.get("pharmacy_id"),request.form.get("reason","").strip())
            flash("Recommendation sent to buyer.","success")
            return redirect(url_for("ngo.manage"))
        except ValueError as e:
            flash(str(e),"danger")
            return redirect(url_for("ngo.suggest",rid=rid))
    return render_template("ngo/recommend.html",r=r,items=inv.byngo(current_user.user_id,r["city"],True),pharmacies=pharm.bycity(r["city"]))
