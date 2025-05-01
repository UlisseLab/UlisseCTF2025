# Telemetry

|         |                            |
| ------- | -------------------------- |
| Authors | Alan Davide Bovo <@AlBovo> |
| Points  | 500                        |
| Tags    | web                        |

## Challenge Description

Elia has just developed a brand-new website to analyze logs at runtime 🧻. Confident in his security skills, he bet his entire house that you won't find the hidden flag... Will you prove him wrong? 🏠🔍

Website: [http://telemetry.challs.ulisse.ovh:6969](http://telemetry.challs.ulisse.ovh:6969)

## Overview

**Telemetry** was a web application that allowed users to upload files (max 10), while internally logging all errors and relevant events into files located at paths like `logs/username/user-uuid.txt`.

The application also featured a template testing endpoint, which let users check whether a given **Jinja2 template** from the `template` directory could be successfully rendered.

## Analysis

The challenge provided a **register** endpoint where users were asked to supply a username and a custom **log filename**. These values were then used to generate a `UUID` that uniquely identified the user’s logfile.

While analyzing the available routes, the most interesting endpoint was `/check`, which attempts to render a Jinja2 template within a **sandboxed environment**:

```python
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
```

This endpoint, however, is **not directly vulnerable**, the use of `secure_filename` and the strict reliance on files inside the `templates/` directory (which users cannot modify) prevents straightforward exploitation.

A more interesting function was the **404 error handler**, which logs failed page accesses:

```python
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
```

This function logs the full, **unquoted URL path** to the user’s log file. However, the log path is constructed using:

```python
os.path.join('logs', user[1], user[0] + '.txt')
```

If the **username** is set to a directory traversal string like `../`, the path becomes:

```
logs/../<uuid>.txt -> <uuid>.txt
```

This effectively allows the user to **break out of the `logs/` directory** and write files into unintended locations, making it vulnerable to **Path traversal** and **template injection**, especially if later rendered or included by the application.

## Exploit

Once the vulnerabilities were understood, the exploitation path was pretty straightforward.
An attacker could register with a **username** like `../templates/` and a random **log filename** (e.g., `fsafsafsasfa`).

This causes the log file to be created at:

```
templates/<uuid>.txt
```

Since the `UUID` is deterministically derived from the attacker-controlled log filename, the attacker **knows the exact name** of the file they are writing into. At this point, the attacker has achieved a **path traversal** that places an arbitrary file directly inside the `templates/` directory.

### Exploiting Blind SSTI

With the ability to write into `templates/`, and the `/check` endpoint acting as a **Jinja2 rendering oracle**, the attacker can now abuse **blind Server-Side Template Injection (SSTI)**.

By crafting malicious payloads and injecting them into their log file (via 404 requests), the attacker can trigger rendering by submitting the filename to `/check`.

To extract the flag, a **blind error-based character-by-character brute-force** can be performed. For example:

```jinja2
{{ 'lol' if config['FLAG'][x] == 'y' else raise('lol') }}
```

This payload accesses `config['FLAG']` and compares the character at index `x` with the guessed character `'y'`.
If the guess is incorrect, an exception is raised and the render fails. If correct, the render succeeds.

By iterating over each character position and all printable characters, the attacker can recover the flag using **only the success/failure feedback**.
