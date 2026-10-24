from flask import Blueprint,render_template,request,redirect,url_for,flash,session
from flask_login import login_user,logout_user,current_user
from werkzeug.security import check_password_hash,generate_password_hash
from models import user,ngo
from util import fixcity,setcity,getcity
import config
bp=Blueprint("auth",__name__,url_prefix="/auth")
@bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("common.dash"))
    if request.method=="POST":
        email=request.form.get("email","").strip()
        pw=request.form.get("password","")
        u=user.byemail(email)
        if u and check_password_hash(u["password_hash"],pw):
            if not u["is_approved"]:
                if u["role"]=="ngo":
                    flash("Your NGO account is awaiting administrator approval.","warning")
                else:
                    flash("Your account is pending approval.","warning")
                return redirect(url_for("auth.login"))
            login_user(user.account(u))
            if u.get("city"):
                setcity(u["city"])
            return redirect(url_for("common.dash"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")
@bp.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("common.dash"))
    if request.method=="POST":
        f=request.form
        name=f.get("name","").strip()
        email=f.get("email","").strip()
        pw=f.get("password","")
        role=f.get("role","")
        city=fixcity(f.get("city"))
        phone=f.get("phone","").strip() or None
        pin=f.get("pincode","").strip() or None
        loc=f.get("locality","").strip() or None
        if role not in("user","ngo"):
            flash("Invalid role selected.","danger")
            return redirect(url_for("auth.register"))
        if not name or not email or not pw or not city:
            flash("Name, email, password and city are required.","danger")
            return redirect(url_for("auth.register"))
        if "@" not in email or "." not in email.split("@")[-1] or len(email)<5:
            flash("Please enter a valid email address.","danger")
            return redirect(url_for("auth.register"))
        if len(pw)<6:
            flash("Password must be at least 6 characters long.","danger")
            return redirect(url_for("auth.register"))
        if len(pw)>128:
            flash("Password cannot exceed 128 characters.","danger")
            return redirect(url_for("auth.register"))
        if pw!=f.get("confirm_password"):
            flash("Passwords do not match.","danger")
            return redirect(url_for("auth.register"))
        if user.byemail(email):
            flash("Email already registered.","danger")
            return redirect(url_for("auth.register"))
        uid=user.create(name,email,generate_password_hash(pw),role,phone,city,pin,loc)
        if role=="ngo":
            ngo.create(uid,f.get("ngo_name") or name,f.get("registration_number"),city,loc)
            flash("Registration submitted! Your NGO account is pending admin approval.","success")
        else:
            flash("Registration successful! You can now log in.","success")
        return redirect(url_for("auth.login"))
    return render_template("register.html",cities=config.cities,city=getcity())
@bp.route("/logout")
def logout():
    session.pop("city",None)
    session.pop("unread",None)
    session.pop("unread_ts",None)
    logout_user()
    return redirect(url_for("common.index"))
