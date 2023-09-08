from flask import Flask, session, redirect, url_for as url, request, render_template as render, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from http.client import HTTPException
from passlib.hash import argon2
from datetime import timedelta
from helpers import settings
import flask_socketio
import flask_session
import functools
import tempfile
import secrets
import uuid
import cs50



app = Flask(__name__)

app.config.update({
	"TEMPLATES_AUTO_RELOAD": True,
	"SESSION_FILE_DIR": tempfile.mkdtemp(),
	"SESSION_TYPE": "filesystem",
	"SESSION_PERMAMENT": True,
	"PERMANENT_SESSION_LIFETIME": timedelta(hours = 12),
	"JSONIFY_PRETTYPRINT_REGULAR": True,
	"SECRET_KEY": secrets.token_hex()
})

flask_session.Session(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

socket = flask_socketio.SocketIO(app)

# ====== Begin Wrapper Definitions ======

def login_req(func):
	@functools.wraps(func)
	def deced(*args, **kwargs):
		with app.test_request_context():
			if session.get("p_id") != settings.DB.execute("SELECT p_id FROM user WHERE id = ?", session.get("id")):
				return redirect(url("login"))
			return func(*args, **kwargs)
	return deced

@login_req
def admin_req(func):
	@functools.wraps(func)
	def deced(*args, **kwargs):
		with app.test_request_context():
			if not session.get("controls"):
				return abort(404)
			return func(*args, **kwargs)
	return deced

# ====== End Wrapper Definitions ======

# ====== Begin Route Definitions ======

@app.route('/')
def index(): return "<h1>Hello, world</h1>"

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		form = request.form.to_dict()
		if len(user := settings.DB.execute("SELECT * FROM user WHERE username = ?", form.username)) == 1 and argon2.verify(form.password, user.password_):
			session.update({"id": user.id, "p_id": user.p_id, "controls": user.controls})
			return redirect(url("index"))
		return render("auth/login.html", error = True)
	return render("auth/login.html")

@admin_req
@app.route('/register', methods = ['GET', 'POST'])
def new_user():
	if request.method == 'POST':
		form = request.form.to_dict()
		if len(settings.DB.execute("SELECT * FROM user WHERE username = ?", form.username)) == 0:
			data = {"id": uuid.uuid4(), 
				"username": form.username, 
				"password": argon2.using(**settings.HASH_SETTINGS).hash(form.password), 
				"p_id": uuid.uuid4(), 
				"admin": form.admin
			}
			user = settings.DB.execute("INSERT INTO user (id, username, password_, p_id, controls) VALUES (:id, :username, :password, :p_id, :controls)", **data)
			session.update({"id": user.id, "p_id": user.p_id, "controls": user.controls})
			return redirect(url("index"))
		return render("auth/register.html", error = True)
	return render("auth/register.html")

# ====== End Route Definitions ======

# ====== Begin API Routes ======

@app.route('/api')
def api():
	pass

# ====== End API Routes ======

@app.errorhandler(HTTPException)
def httperrhandler(err):
	print(err)