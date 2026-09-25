import os
from flask import Flask,render_template
from flask_login import LoginManager,current_user
import config
from models import user,notif
from routes import auth,common,seller,buyer,ngo,admin
from util import getcity,free
app=Flask(__name__,static_folder="public",static_url_path="")
app.config.from_object(config)
lm=LoginManager(app)
lm.login_view="auth.login"
lm.login_message="Please log in to access this page."
lm.login_message_category="info"
@lm.user_loader
def loaduser(uid):
    data=user.byid(int(uid))
    return user.account(data) if data else None
@app.context_processor
def ctx():
    unread=notif.unread(current_user.user_id) if current_user.is_authenticated else 0
    return {"cities":config.cities,"city":getcity(),"free":free(),"unread":unread}
app.register_blueprint(auth.bp)
app.register_blueprint(common.bp)
app.register_blueprint(seller.bp)
app.register_blueprint(buyer.bp)
app.register_blueprint(ngo.bp)
app.register_blueprint(admin.bp)
@app.errorhandler(403)
def e403(err):
    return render_template("errors/403.html"),403
@app.errorhandler(404)
def e404(err):
    return render_template("errors/404.html"),404
@app.errorhandler(500)
def e500(err):
    return render_template("errors/500.html"),500
if(__name__=="__main__"):
    app.run(debug=os.environ.get("FLASK_DEBUG","1")=="1",host="127.0.0.1",port=5000)
