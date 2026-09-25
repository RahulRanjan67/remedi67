from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from util import needrole,daysleft,getcity,scope,markexp,toint
from models import don,med,contact,user
bp=Blueprint("seller",__name__,url_prefix="/seller")
@bp.route("/dashboard")
@login_required
@needrole("seller")
def dash():
    name=user.donor(current_user.user_id)[0]
    waiting=len([c for c in contact.byseller(current_user.user_id,None) if c["status"]=="pending"])
    return render_template("seller/dashboard.html",stats=don.stats(current_user.user_id,None),tier=name,waiting=waiting)
@bp.route("/donate",methods=["GET","POST"])
@login_required
@needrole("seller")
def donate():
    if(request.method=="POST"):
        f=request.form
        name=f.get("medicine_name","").strip()
        exp=f.get("expiry_date","").strip()
        cond=f.get("condition_status")
        cat=f.get("category_id","")
        if(not name):
            flash("Medicine name is required.","danger")
            return redirect(url_for("seller.donate"))
        qty=toint(f.get("quantity"))
        if(qty<1):
            flash("Quantity must be a positive number.","danger")
            return redirect(url_for("seller.donate"))
        if(cond not in("sealed","opened","partial")):
            flash("Please choose the medicine condition.","danger")
            return redirect(url_for("seller.donate"))
        if(daysleft(exp)<60):
            flash("Medicines expiring in less than 60 days cannot be donated.","danger")
            return redirect(url_for("seller.donate"))
        mid=med.getid(name,int(cat) if cat.isdigit() else None)
        don.create(current_user.user_id,mid,qty,f.get("batch_number","").strip(),exp,getcity(),f.get("locality","").strip(),cond)
        flash("Donation submitted! It is now pending NGO verification.","success")
        return redirect(url_for("seller.mine"))
    return render_template("seller/donate.html",categories=med.cats(),medicines=med.every())
@bp.route("/donations")
@login_required
@needrole("seller")
def mine():
    return render_template("seller/donations.html",donations=markexp(don.bysel(current_user.user_id,None)))
@bp.route("/contact-requests")
@login_required
@needrole("seller")
def contacts():
    return render_template("seller/contact_requests.html",requests=contact.byseller(current_user.user_id,None))
@bp.route("/contact-requests/<int:cid>/<action>",methods=["POST"])
@login_required
@needrole("seller")
def reply(cid,action):
    if(action in("approve","reject")):
        try:
            contact.reply(cid,current_user.user_id,action)
            flash(f"Contact request {action}d.","success")
        except ValueError as e:
            flash(str(e),"danger")
    return redirect(url_for("seller.contacts"))
