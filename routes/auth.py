from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,current_user
from werkzeug.security import check_password_hash,generate_password_hash
from models import user,ngo
from util import fixcity,setcity
bp=Blueprint("auth",__name__,url_prefix="/auth")
@bp.route("/login",methods=["GET","POST"])
def login():
    if(current_user.is_authenticated):
        return redirect(url_for("common.dash"))
    if(request.method=="POST"):
        email=request.form.get("email","").strip()
        pw=request.form.get("password","")
        u=user.byemail(email)
        if(u and check_password_hash(u["password_hash"],pw)):
            if(not u["is_approved"]):
                if(u["role"]=="ngo"):
                    flash("Your NGO account is awaiting administrator approval.","warning")
                else:
                    flash("Your account is pending approval.","warning")
                return redirect(url_for("auth.login"))
            login_user(user.account(u))
            setcity(u["city"])
            return redirect(url_for("common.dash"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")
@bp.route("/register",methods=["GET","POST"])
def register():
    if(current_user.is_authenticated):
        return redirect(url_for("common.dash"))
    if(request.method=="POST"):
        f=request.form
        name=f.get("name","").strip()
        email=f.get("email","").strip()
        pw=f.get("password","")
        role=f.get("role","")
        city=fixcity(f.get("city"))
        if(role not in("buyer","seller","ngo")):
            flash("Invalid role selected.","danger")
            return redirect(url_for("auth.register"))
        if(not name or not email or not pw or not city):
            flash("All required fields must be filled and a supported city selected.","danger")
            return redirect(url_for("auth.register"))
        if(pw!=f.get("confirm_password")):
            flash("Passwords do not match.","danger")
            return redirect(url_for("auth.register"))
        if(user.byemail(email)):
            flash("Email already registered.","danger")
            return redirect(url_for("auth.register"))
        uid=user.create(name,email,generate_password_hash(pw),role,f.get("phone"),city,f.get("pincode"),f.get("locality"))
        if(role=="ngo"):
            ngo.create(uid,f.get("ngo_name") or name,f.get("registration_number"),city,f.get("locality"))
            flash("Registration submitted! Your NGO account is pending admin approval.","success")
        else:
            flash("Registration successful! You can now log in.","success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")
@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("common.index"))
