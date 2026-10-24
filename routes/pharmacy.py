from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from flask_login import login_required,current_user
from util import needrole,toint,scope,getcity
from models import pharm,req,notif
bp=Blueprint("pharmacy",__name__,url_prefix="/pharmacy")
def get_my_pharmacy():
    p=pharm.byuser(current_user.user_id)
    if not p:
        candidates=pharm.bycity(getcity())
        p=candidates[0] if candidates else None
    return p
@bp.route("/dashboard")
@login_required
@needrole("pharmacy","developer","admin")
def dash():
    p=get_my_pharmacy()
    if not p:
        flash("No active pharmacy record is linked to your account.","warning")
        return render_template("pharmacy/dashboard.html",pharmacy=None,stats={"total":0,"waiting":0,"ready":0,"dispensed":0},requests=[])
    pstats=req.pharmacy_stats(p["pharmacy_id"])
    requests=req.bypharmacy(p["pharmacy_id"])
    return render_template("pharmacy/dashboard.html",pharmacy=p,stats=pstats,requests=requests)
@bp.route("/ready/<int:rid>",methods=["POST"])
@login_required
@needrole("pharmacy","developer","admin")
def ready(rid):
    p=get_my_pharmacy()
    if not p:
        abort(403)
    try:
        req.ready_pharmacy(rid,p["pharmacy_id"],current_user.user_id)
        flash(f"Request #{rid} marked ready for patient pickup.","success")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(request.referrer or url_for("pharmacy.dash"))
@bp.route("/dispense/<int:rid>",methods=["POST"])
@login_required
@needrole("pharmacy","developer","admin")
def dispense(rid):
    p=get_my_pharmacy()
    if not p:
        abort(403)
    try:
        req.dispense_pharmacy(rid,p["pharmacy_id"],current_user.user_id)
        flash(f"Request #{rid} successfully dispensed and completed.","success")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(request.referrer or url_for("pharmacy.dash"))
@bp.route("/verify-pass",methods=["GET","POST"])
@login_required
@needrole("pharmacy","developer","admin","ngo")
def verify():
    rid=toint(request.form.get("request_id") or request.args.get("rid"))
    record=None
    if rid>0:
        record=req.byid(rid)
        if not record:
            flash(f"No medicine request found with ID #{rid}.","warning")
        elif record.get("fetch_method")!="pharmacy":
            flash(f"Request #{rid} was requested via {record.get('fetch_method','direct')} exchange, not pharmacy pickup.","info")
    return render_template("pharmacy/verify_pass.html",record=record,searched_id=rid or "")
