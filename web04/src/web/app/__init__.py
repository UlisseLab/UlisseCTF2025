import datetime
import os
import secrets
import sys
import traceback
import uuid
from flask import Flask, g, json, jsonify
from flask import render_template, request, make_response, redirect, url_for, abort
from itsdangerous import URLSafeSerializer
import mysql
import mysql.connector
from . import utils
from .utils import cache_control, vary, with_user
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["VERSION"] = os.getenv("VERSION") or "1.0"
app.config["POW_DIFFICULTY"] = 18

# Max upload size of 32kb
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.get("/")
@cache_control(public=True, max_age=60*60*10, immutable=True)
@vary(["Cookie"])
@with_user(required=False)
def index(user_id: uuid.UUID):
    if user_id is None:
        return render_template("index.html")

    return redirect(url_for("view_posts", creator_id=user_id))


@app.route("/register", methods=["GET", "POST"])
@cache_control(public=True, max_age=60*60, immutable=False)
def register():
    if request.method == "GET":
        error = request.args.get("error", None)
        return render_template("register.html", error=error)

    elif request.method == "POST":
        username = request.form.get("username", default=None, type=str)
        password = request.form.get("password", default=None, type=str)
        if not username or not password:
            return make_response(render_template("register.html", error="Missing username or password"), 400)

        try:
            db = utils.open_connection_and_get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO USERS (username, password) VALUES (%s, %s)",
                    (username, password)
                )
            db.commit()
        except mysql.connector.IntegrityError as e:
            print(e, file=sys.stderr)
            return make_response(render_template("register.html", error="Username already exists"), 400)
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
@cache_control(public=True, max_age=60*60)
def login():
    if request.method == "GET":
        error = request.args.get("error", None)
        return render_template("login.html", error=error)
    elif request.method == "POST":
        username = request.form.get("username", default=None, type=str)
        password = request.form.get("password", default=None, type=str)
        if username is None or password is None:
            return abort(400)

        db = utils.open_connection_and_get_db()
        with db.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM USERS WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
        if not user:
            return redirect(url_for("login", error="Invalid credentials"))

        resp = redirect(url_for("view_posts", creator_id=user["id"]))
        resp.set_cookie("session", URLSafeSerializer(app.secret_key).dumps(
            user["id"]), path="/", httponly=True, samesite="Strict")
        return resp


@app.route("/posts/new", methods=["GET", "POST"])
@cache_control(public=True, max_age=60*60, immutable=True)
@vary(["Cookie"])
@with_user(required=True)
def new_post(user_id: uuid.UUID):
    if request.method == "GET":
        return render_template("post/new.html")
    elif request.method == "POST":
        title = request.form.get("title", default=None, type=str)
        content = request.form.get("content", default=None, type=str)
        if not title or not content:
            return abort(422)

        db = utils.open_connection_and_get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO POSTS(user_id, title, content) VALUES (%s, %s, %s)",
                (str(user_id), title, content)
            )
            db.commit()
        return redirect(url_for("index"))


@app.get("/posts/<uuid:creator_id>/view")
@cache_control(no_store=True, public=False)
@with_user(required=False)
def view_posts(creator_id: uuid.UUID, user_id: uuid.UUID):
    return render_template(
        "post/view.html",
        posts=utils.get_posts_of(user_id),
        show_actions=creator_id and creator_id == user_id
    )


@app.get("/posts/view/<uuid:post_id>")
@cache_control(public=False, no_store=True)
@with_user(required=False)
def view_post(post_id: uuid.UUID, user_id: uuid.UUID | None):
    post = utils.get_post_by_id(post_id, notes_by=user_id)
    if not post:
        return abort(404)

    css = utils.get_css(user_id)
    return render_template("/post/view.html", posts=[post],
                           show_actions=user_id and str(
                               user_id) == post["user_id"],
                           css=css)


@app.post("/posts/view/<uuid:post_id>")
@with_user(required=True)
def new_comment(post_id: uuid.UUID, user_id: uuid.UUID | None):
    note = request.form.get("note", None)
    if not note:
        return redirect(url_for("view_post", post_id=post_id))

    try:
        db = utils.open_connection_and_get_db()
        with db.cursor(buffered=True, dictionary=True) as conn:
            conn.execute("INSERT INTO NOTES(user_id, post_id, content) VALUES(%s, %s, %s)",
                         (str(user_id), str(post_id), note))
            db.commit()
    except mysql.connector.Error as e:
        print(traceback.format_exception(e), file=sys.stderr, flush=True)
        db.rollback()
        return abort(404)

    return redirect(url_for("view_post", post_id=post_id))


@app.post("/posts/delete/<uuid:post_id>")
@with_user(required=True)
def delete_post(post_id: uuid.UUID, user_id: uuid.UUID):
    db = utils.open_connection_and_get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM POSTS WHERE id=%s AND user_id=%s",
                       (str(post_id), str(user_id)))
        db.commit()
        if cursor.rowcount == 0:
            return abort(404)

    return redirect(url_for("view_posts", creator_id=user_id))


@app.post("/posts/share/<uuid:post_id>")
@with_user(required=True)
def share_post(post_id: uuid.UUID, user_id: uuid.UUID):
    post = utils.get_post_by_id(post_id)
    if not post or post["user_id"] != str(user_id):
        return abort(404)

    try:
        nonce = request.json["nonce"]
        if not utils.verify_pow(user_id, nonce):
            raise ValueError("Invalid PoW")
    except Exception as e:
        print(e, file=sys.stderr, flush=True)
        return jsonify({
            "msg": "Invalid PoW"
        }), 400

    utils.start_admin(post_id)
    return jsonify({
        "msg": "Success"
    })


@app.get('/profile')
@cache_control(public=False, no_store=True, immutable=False)
@vary(["Cookie"])
@with_user(required=True)
def profile(user_id: uuid.UUID):
    user = utils.get_user(user_id)

    return render_template("profile.html", user=user)


@app.post('/profile/upload_css')
@with_user(required=True)
def upload_css(user_id: uuid.UUID):

    if 'css_file' not in request.files:
        return abort(400)

    css_file = request.files['css_file']
    version = hashlib.file_digest(css_file, "sha1").hexdigest()
    path = os.path.join(app.static_folder or "static",
                        "uploads", f"{user_id}.css")
    css_file.save(path)
    utils.save_css(user_id, version)
    return redirect(url_for("profile"))


@app.post('/get-challenge')
@with_user(required=True)
def get_challenge(user_id: uuid.UUID):
    chall = secrets.token_hex(8)
    db = utils.open_connection_and_get_db()
    with db.cursor() as conn:
        conn.execute("UPDATE USERS SET pow_challenge=%s WHERE id=%s",
                     (chall, str(user_id)))
        db.commit()

    return jsonify({
        "challenge": chall,
        "difficulty": app.config["POW_DIFFICULTY"]
    })
