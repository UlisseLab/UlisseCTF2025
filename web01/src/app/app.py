from flask import Flask, request, session, render_template, redirect, send_from_directory, flash
from jinja2.sandbox import SandboxedEnvironment
from werkzeug.utils import secure_filename
from urllib.parse import unquote
from flask_session import Session
import os, time, uuid

app = Flask(__name__)
app.config['FLAG'] = os.getenv('FLAG')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 1024
MAX_FILES = os.getenv('MAX_FILES', 10)

class JinjaEnvironment(SandboxedEnvironment):
    # Simply wraps jinja's sandboxed environment so that it can be used with flask
    def __init__(self, app: Flask, **options) -> None:
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        SandboxedEnvironment.__init__(self, **options)
        self.app = app

app.jinja_environment = JinjaEnvironment
Session(app)

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('user', None):
            return 'Unauthorized', 401
        return f(session['user'], *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['user']
    log_file = request.form['log']

    if len(log_file) != 32:
        flash('Invalid log filename length', 'danger')
        return redirect('/')
    
    user_id = str(uuid.UUID(log_file))
    log_file = user_id + '.txt'
    
    if os.path.exists(os.path.join('logs', username, log_file)):
        flash('User/Log already exists', 'danger')
        return redirect('/')
    
    session['user'] = (user_id, username)
    session['files'] = MAX_FILES
    
    os.makedirs(os.path.join('logs', username), exist_ok=True)
    with open(os.path.join('logs', username, log_file), 'w') as f:
        f.write(f'[{time.time()}] - Log file: {user_id}.txt\n')
        f.write(f'[{time.time()}] - User logged in\n')
    
    return redirect('/upload')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload(user):
    if request.method == 'GET':
        return render_template('upload.html')
    
    if int(session['files']) == 0:
        flash('You have reached the maximum number of files', 'danger')
        return redirect('/upload')

    session['files'] = int(session['files']) - 1
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    os.makedirs(os.path.join('uploads', user[0]), exist_ok=True)
    file.save(os.path.join('uploads', user[0], filename))
    
    if not os.path.exists(os.path.join('logs', user[1], user[0] + '.txt')):
        session.clear()
        return 'Unauthorized', 401
    
    with open(os.path.join('logs', user[1], user[0] + '.txt'), 'a') as f:
        f.write(f'[{time.time()}] - File uploaded: {filename}\n')
    
    return redirect(f'/uploads/{filename}')

@app.route('/uploads/<filename>')
@login_required
def showfile(user, filename):
    username = user[0]
    if os.path.exists(os.path.join('uploads', username, filename)):
        return send_from_directory('uploads', os.path.join(username, filename), mimetype='text/plain')
    flash('File not found', 'danger')
    return redirect('/upload')

@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'GET':
        return render_template('check.html')
    
    template = secure_filename(request.form['template'])
    if not os.path.exists(os.path.join('templates', template)):
        flash('Template not found', 'danger')
        return redirect('/check')
    try:
        render_template(template)
        flash('Template rendered successfully', 'success')
    except:
        flash('Error rendering template', 'danger')
    return redirect('/check')
    
@app.errorhandler(404)
def page_not_found(e):
    if user := session.get('user', None):
        if not os.path.exists(os.path.join('logs', user[1], user[0] + '.txt')):
            session.clear()
            return 'Page not found', 404
        with open(os.path.join('logs', user[1], user[0] + '.txt'), 'a') as f:
            f.write(f'[{time.time()}] - Error at page: {unquote(request.url)}\n')
        return redirect('/')
    return 'Page not found', 404