import datetime
import hashlib
import sys
import traceback
from flask import (
    abort,
    current_app,
    make_response,
    Response,
    redirect,
    request,
    url_for,
)
from functools import wraps
import uuid
from itsdangerous import URLSafeSerializer
import mysql.connector
from flask import g
import mysql.connector.types
import requests
import os
# Update the connection to MySQL

mysql.connector.pooling.PooledMySQLConnection


def open_connection_and_get_db() -> mysql.connector.MySQLConnection:
    db: mysql.connector.MySQLConnection = getattr(g, "db", None)  # type: ignore
    if db is None:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            pool_size=10,
            pool_name="default",
        )
        g.db = db
    return db


def get_user(user_id: uuid.UUID):
    db = open_connection_and_get_db()
    with db.cursor(buffered=True, dictionary=True) as conn:
        conn.execute("SELECT username, css, id FROM USERS WHERE id=%s", (str(user_id),))
        return conn.fetchone()


def get_css(user_id: uuid.UUID | None):
    if user_id is None:
        return None
    db = open_connection_and_get_db()
    with db.cursor(buffered=True, dictionary=True) as cursor:
        cursor.execute("SELECT css FROM USERS where id=%s", (str(user_id),))
        res = cursor.fetchone()

    if not res or "css" not in res or not res["css"]:
        return None
    return {"version": res["css"], "path": f"uploads/{user_id}.css"}


def save_css(user_id: uuid.UUID, version: str):
    db = open_connection_and_get_db()
    with db.cursor() as cursor:
        cursor.execute("UPDATE USERS SET css=%s WHERE id=%s", (version, str(user_id)))
        db.commit()


def get_posts_of(user_id: uuid.UUID) -> list[dict]:
    db = open_connection_and_get_db()
    # Use dictionary cursor for returning dictionaries
    with db.cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute("SELECT * FROM POSTS WHERE user_id=%s", (str(user_id),))
        return cursor.fetchall()  # type: ignore


def get_post_by_id(
    post_id: uuid.UUID, notes_by: uuid.UUID | None = None
) -> dict | None:
    db = open_connection_and_get_db()
    with db.cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute("SELECT * FROM POSTS WHERE id=%s", (str(post_id),))
        post = cursor.fetchone()  # type: ignore
        if post and notes_by:
            cursor.execute(
                "SELECT * FROM NOTES WHERE post_id=%s and user_id=%s",
                (str(post_id), str(notes_by)),
            )
            notes = cursor.fetchall()
            post["notes"] = notes
        return post


def with_user(required: bool = False):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            s = URLSafeSerializer(current_app.secret_key)
            user_id = None
            try:
                sess = request.cookies.get("session")
                if sess:
                    user_id = uuid.UUID(s.loads(sess))
            except Exception as e:
                print(e, file=sys.stderr)

            if not user_id and required:
                return redirect(
                    url_for("register", error="You must be logged in to do this action")
                )
            return f(*args, user_id=user_id, **kwargs)

        return decorated

    return decorator


def cache_control(
    public: bool = True,
    max_age: int = None,
    immutable: bool = False,
    no_store: bool = False,
    **directives,
):
    """
    Decorator that adds a Cache-Control header to the response.

    Parameters:
      public (bool): If True, set directive to "public", else "private".
      max_age (int): Number of seconds for max-age.
      immutable (bool): If True, add "immutable".
      no_store (bool): If True, add "no-store".
      **directives: Additional Cache-Control directives, where key is the directive and the value is its value (or None if no value needed).

    Example:
      @cache_control(public=True, max_age=3600, immutable=True)
      def view_func():
          ...

    This would produce:
      Cache-Control: public, max-age=3600, immutable
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rv = f(*args, **kwargs)
            if not isinstance(rv, Response):
                rv = make_response(rv)

            if request.method != "GET" or rv.status_code >= 400:
                return rv
            directives_list = []

            # Determine public/private
            directives_list.append("public" if public else "private")
            if no_store:
                directives_list.append("no-store")
            # Handle max_age if set
            if max_age is not None:
                directives_list.append(f"max-age={max_age}")
            # Handle immutable if set
            if immutable:
                directives_list.append("immutable")
            # Handle any additional directives
            for key, value in directives.items():
                key = key.replace("_", "-")
                if value is None or value is True:
                    directives_list.append(key)
                else:
                    directives_list.append(f"{key}={value}")

            # Set the header
            rv.headers["Cache-Control"] = ", ".join(directives_list)
            return rv

        return decorated_function

    return decorator


def vary(headers: list[str]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rv = f(*args, **kwargs)
            if not isinstance(rv, Response):
                rv = make_response(rv)
            rv.headers["Vary"] = ", ".join(headers)
            return rv

        return decorated_function

    return decorator


def start_admin(post_id: uuid.UUID):
    chall = "http://web04-nginx:8080"
    requests.post(
        f"http://{os.getenv('ADMIN_HOST')}:5000/",
        headers={
            "X-Auth": os.getenv("ADMIN_AUTH_TOKEN"),
            "Content-Type": "application/json",
        },
        json={
            "actions": [
                {
                    "type": "request",
                    "url": f"{chall}/login",
                    "method": "POST",
                    "data": f"username=admin&password={os.getenv('ADMIN_AUTH_TOKEN')}",
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                },
                {
                    "type": "request",
                    "url": f"{chall}/posts/view/{str(post_id)}",
                },
                {
                    "type": "type",
                    "element": "#note",
                    "value": os.getenv("FLAG"),
                    "delay": 0.1,
                },
                {
                    "type": "sleep",
                    "time": 1,
                },
                {"type": "click", "element": "button#submit-note"},
            ],
            "timeout": 60,
        },
    )


# NOT PART OF THE CHALLENGE


def verify_pow(user_id: uuid.UUID, nonce: int) -> bool:
    try:
        db = open_connection_and_get_db()
        with db.cursor(buffered=True, dictionary=True) as conn:
            conn.execute(
                "SELECT pow_challenge FROM USERS WHERE id=%s FOR UPDATE",
                (str(user_id),),
            )
            res = conn.fetchone()
            if not res or not (chall := res.get("pow_challenge")):
                raise ValueError("Missing challenge")

            val: str = chall + str(nonce)
            hash = hashlib.sha256(val.encode()).digest()
            fail = int.from_bytes(hash, "big") >> (
                256 - current_app.config["POW_DIFFICULTY"]
            )
            conn.execute(
                "UPDATE USERS SET pow_challenge=NULL where id=%s", (str(user_id),)
            )
            db.commit()
            return not fail
    except Exception as e:
        db.rollback()
        print(traceback.format_exception(e), file=sys.stderr, flush=True)
        return False
