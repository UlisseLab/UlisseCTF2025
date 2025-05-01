from flask import Flask, render_template, request
from markupsafe import Markup
import os
import re
import markdown

app = Flask(__name__)
POSTS_DIR = "posts"
FLAG_LAT = os.getenv("FLAG_LAT", "11.111")
FLAG_LON = os.getenv("FLAG_LON", "11.111")


def load_post(post_id):
    path = os.path.join(POSTS_DIR, f"{post_id}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = markdown.markdown(f.read(), extensions=["fenced_code", "tables"])
            return Markup(html)
    return None

# @app.route("/")
# def index():
#     post_ids = sorted(int(f.split(".")[0]) for f in os.listdir(POSTS_DIR) if f.endswith(".md"))
#     return render_template("index.html", post_ids=post_ids)

@app.route("/")
def index():
    posts = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            match = re.match(r"(\d{4})_(\d{2})_(\d{2})_(.+)\.md", filename)
            if match:
                year, month, day, slug = match.groups()
                date = f"{year}-{month}-{day}"
                title = slug.replace("_", " ").title()
                posts.append({
                    "filename": filename,
                    "date": date,
                    "title": title
                })
    posts.sort(key=lambda x: x["date"], reverse=True)
    print(posts)
    return render_template("index.html", posts=posts)



# @app.route("/post/<int:post_id>")
# def post(post_id):
#     content = load_post(post_id)
#     if content:
#         return render_template("post.html", content=content)
#     return "Post not found", 404

@app.route("/post/<filename>")
def post(filename):
    path = os.path.join(POSTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = markdown.markdown(f.read(), extensions=["fenced_code", "tables"])
            return render_template("post.html", content=Markup(content))
    return "Post not found", 404


@app.route("/whoami")
def whoami():
    return render_template("whoami.html")

@app.route("/getsecret", methods=["GET", "POST"])
def getsecret():
    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat.strip() == FLAG_LAT and lon.strip() == FLAG_LON:
            flag = os.getenv("ULISSE_FLAG", "ULSCTF{default_flag}")
            return render_template("getsecret.html", success=True, flag=flag)

        else:
            return render_template("getsecret.html", error=True)
    return render_template("getsecret.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7778)
