"""Generate a static version of selected templates (login) and copy static assets.
This does not import the Flask app to avoid heavy runtime imports.
"""
import os
import sys
import warnings
from jinja2 import Environment, FileSystemLoader
import shutil

ROOT = os.path.dirname(__file__)
TEMPLATES = os.path.join(ROOT, 'templates')
STATIC = os.path.join(ROOT, 'static')
OUT = os.path.join(ROOT, 'build')

os.makedirs(OUT, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES))


def fake_url_for(endpoint, filename=None):
    """Minimal `url_for` used while rendering templates for static export.

    Maps:
    - static -> static/<filename>
    - login -> /
    - register -> /register.html
    Unmapped endpoints emit a warning and return '#'.
    """
    if endpoint == 'static' and filename:
        return f'static/{filename}'

    # Known app endpoints mapped to static pages
    if endpoint in ('login', 'auth.login'):
        return '/'  # root serves the login page
    if endpoint in ('register', 'auth.register'):
        return '/register.html'

    # If endpoint is None (e.g. request.endpoint), return root
    if endpoint is None:
        return '/'

    # Warn about unmapped endpoints to aid debugging
    warnings.warn(f"freeze_static: unmapped endpoint '{endpoint}' — returning '#'", UserWarning)
    return '#'


def get_flashed_messages():
    return []


class _AnonymousUser:
    is_authenticated = False


class _FakeRequest:
    def __init__(self):
        self.endpoint = None


env.globals['url_for'] = fake_url_for
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['request'] = _FakeRequest()

# Render login page as the root index
tpl = env.get_template('login.html')
html = tpl.render(current_user=_AnonymousUser())
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)

# If templates contain a register page, render it too so links work
try:
    tpl_reg = env.get_template('register.html')
    html_reg = tpl_reg.render(current_user=_AnonymousUser())
    with open(os.path.join(OUT, 'register.html'), 'w', encoding='utf-8') as f:
        f.write(html_reg)
except Exception:
    # If there's no register template, it's fine; links will show '#'
    pass

# Copy static assets
if os.path.exists(STATIC):
    dest_static = os.path.join(OUT, 'static')
    if os.path.exists(dest_static):
        shutil.rmtree(dest_static)
    shutil.copytree(STATIC, dest_static)

print('Static site generated in', OUT)
