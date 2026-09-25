from flask import Blueprint,render_template,request,redirect,url_for,flash,jsonify,abort
from flask_login import login_required,current_user
from db import query
from models import inv,urgent,notif,pharm,don,user
from util import fixcity,setcity,scope,free,markexp
bp=Blueprint("common",__name__)
@bp.route("/")
def index():
    city=scope()
    stock=inv.stats(city)
    stats={"verified":don.count("verified",city),"avail":stock["avail"],"users":user.stats(city)["total"],"fulfilled":urgent.count("fulfilled",city)}
    return render_template("home.html",stats=stats,label=city or "All cities")
@bp.route("/city",methods=["POST"])
def pick():
    city=fixcity(request.form.get("city"))
    if(not city):
        flash("Please select a supported city.","danger")
    else:
        setcity(city)
    return redirect(request.referrer or url_for("common.index"))
@bp.route("/dashboard")
@login_required
def dash():
    role=current_user.role
    if(role=="developer"):
        return redirect(url_for("admin.devdash"))
    return redirect(url_for(role+".dash"))
@bp.route("/search")
def search():
    q=request.args.get("q","").strip()
    picked=fixcity(request.args.get("city"))
    if(picked and not free()):
        setcity(picked)
    city=scope()
    urgent.refresh(city)
    items=markexp(inv.search(q,request.args.get("category_id"),city,request.args.get("sort","expiry")))
    return render_template("inventory.html",items=items,q=q,sel=city)
@bp.route("/pharmacies")
def pharms():
    city=scope()
    return render_template("pharmacy_lookup.html",pharmacies=pharm.bycity(city),label=city or "all cities")
@bp.route("/pharmacies/search",methods=["POST"])
def pharmfind():
    data=request.get_json(silent=True) or {}
    pin=str(data.get("pincode","")).strip()
    if(pin):
        return jsonify(pharm.bypin(pin,scope()))
    return jsonify(pharm.bycity(scope()))
@bp.route("/pharmacies/register",methods=["GET","POST"])
def pharmadd():
    if(request.method=="POST"):
        f=request.form
        name=f.get("name","").strip()
        address=f.get("address","").strip()
        city=fixcity(f.get("city"))
        pin=f.get("pincode","").strip()
        if(name and address and city and pin):
            pharm.create(name,address,city,pin,f.get("phone","").strip())
            if(not free()):
                setcity(city)
            flash(f"Pharmacy \"{name}\" registered successfully as a designated exchange point.","success")
            return redirect(url_for("common.pharms",city=city))
        flash("Please fill in all required fields.","danger")
    return render_template("register_pharmacy.html")
@bp.route("/notice-board")
def board():
    city=scope()
    return render_template("notice_board.html",needs=urgent.live(city),sel=city,label=city or "all cities")
@bp.route("/profile")
@login_required
def profile():
    tier=None
    count=0
    if(current_user.role=="seller"):
        tier,count=user.donor(current_user.user_id)
    return render_template("profile.html",tier=tier,count=count)
@bp.route("/profile/update",methods=["POST"])
@login_required
def profedit():
    f=request.form
    city=fixcity(f.get("city")) or current_user.city
    user.update(current_user.user_id,f.get("name","").strip() or current_user.name,f.get("phone"),city,f.get("pincode"),f.get("locality"))
    if(not free()):
        setcity(city)
    flash("Profile updated","success")
    return redirect(url_for("common.profile"))
@bp.route("/notifications")
@login_required
def notifs():
    items=notif.mine(current_user.user_id)
    notif.markall(current_user.user_id)
    return render_template("notifications.html",notifications=items)
@bp.route("/status-history/<kind>/<int:eid>")
@login_required
def history(kind,eid):
    if(kind not in("donation","request")):
        abort(404)
    rows=query("SELECT * FROM status_history WHERE entity_type=%s AND entity_id=%s ORDER BY changed_at DESC,history_id DESC",(kind,eid))
    return render_template("status_history.html",history=rows)
