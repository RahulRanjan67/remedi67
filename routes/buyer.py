from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from util import needrole,scope,getcity,markexp,toint
from models import req,contact,urgent,rec,inv,pharm,don,med
bp=Blueprint("buyer",__name__,url_prefix="/buyer")
@bp.route("/dashboard")
@login_required
@needrole("buyer")
def dash():
    return render_template("buyer/dashboard.html",stats=req.buyerstats(current_user.user_id,None))
@bp.route("/requests")
@login_required
@needrole("buyer")
def reqs():
    return render_template("buyer/requests.html",requests=req.bybuyer(current_user.user_id,None))
@bp.route("/request/<int:iid>",methods=["GET","POST"])
@login_required
@needrole("buyer")
def ask(iid):
    item=inv.byid(iid,scope())
    if(not item):
        flash("Item not found in your city.","danger")
        return redirect(url_for("common.search"))
    if(request.method=="POST"):
        method=request.form.get("fetch_method")
        pid=request.form.get("pharmacy_id") if method=="pharmacy" else None
        try:
            req.create(current_user.user_id,iid,toint(request.form.get("quantity")),method,pid)
            flash("Request submitted successfully","success")
            return redirect(url_for("buyer.reqs"))
        except ValueError as e:
            flash(str(e),"danger")
            return redirect(url_for("buyer.ask",iid=iid))
    item=markexp([item])[0]
    return render_template("buyer/request_form.html",item=item,pharmacies=pharm.bycity(item["city"]))
@bp.route("/requests/<int:rid>/cancel",methods=["POST"])
@login_required
@needrole("buyer")
def cancel(rid):
    try:
        req.cancel(rid,current_user.user_id)
        flash("Request cancelled","info")
    except ValueError as e:
        flash(str(e),"danger")
    return redirect(url_for("buyer.reqs"))
@bp.route("/contact-requests")
@login_required
@needrole("buyer")
def contacts():
    return render_template("buyer/contact_requests.html",requests=contact.bybuyer(current_user.user_id,None))
@bp.route("/contact/<int:did>",methods=["POST"])
@login_required
@needrole("buyer")
def reach(did):
    d=don.byid(did,scope())
    if(not d or d["status"]!="verified"):
        flash("Donation not found in your city.","danger")
        return redirect(url_for("common.search"))
    try:
        contact.create(current_user.user_id,d["seller_id"],did)
        flash("Contact request sent to seller.","success")
    except ValueError as e:
        flash(str(e),"warning")
    return redirect(url_for("buyer.contacts"))
@bp.route("/urgent-needs",methods=["GET","POST"])
@login_required
@needrole("buyer")
def needs():
    if(request.method=="POST"):
        name=request.form.get("medicine_name","").strip()
        qty=toint(request.form.get("quantity"))
        if(not name or qty<1):
            flash("Enter a medicine name and a quantity of at least 1.","danger")
        else:
            urgent.create(current_user.user_id,med.getid(name,None),qty,getcity(),current_user.locality or "")
            flash("Urgent need posted successfully.","success")
        return redirect(url_for("buyer.needs"))
    return render_template("buyer/urgent_needs.html",needs=urgent.bybuyer(current_user.user_id,None),city=getcity())
@bp.route("/recommendations")
@login_required
@needrole("buyer")
def recs():
    return render_template("buyer/recommendations.html",recommendations=rec.bybuyer(current_user.user_id,None))
@bp.route("/recommendations/<int:recid>/<action>",methods=["POST"])
@login_required
@needrole("buyer")
def answer(recid,action):
    if(action in("accept","reject")):
        try:
            rec.answer(recid,current_user.user_id,action)
            flash(f"Recommendation {action}ed.","success")
        except ValueError as e:
            flash(str(e),"danger")
    return redirect(url_for("buyer.recs"))
