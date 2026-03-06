"""Generate a static version of selected templates (login) and copy static assets.
This does not import the Flask app to avoid heavy runtime imports.
"""
import os
from jinja2 import Environment, FileSystemLoader
import shutil

ROOT = os.path.dirname(__file__)
TEMPLATES = os.path.join(ROOT, 'templates')
STATIC = os.path.join(ROOT, 'static')
OUT = os.path.join(ROOT, 'build')

os.makedirs(OUT, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES))

# Simple replacement for url_for('static', filename=...)
def fake_url_for(endpoint, filename=None):
    if endpoint == 'static' and filename:
        return f'static/{filename}'
    return '/'

env.globals['url_for'] = fake_url_for
env.globals['get_flashed_messages'] = lambda: []
env.globals['request'] = type('R',(),{'endpoint': None})()

tpl = env.get_template('login.html')
# Render login page as the root index
tpl = env.get_template('login.html')
# Provide a minimal `current_user` object expected by base.html
class _Anon:
    is_authenticated = False

html = tpl.render(current_user=_Anon())
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)

# Copy static assets
if os.path.exists(STATIC):
    dest_static = os.path.join(OUT, 'static')
    if os.path.exists(dest_static):
        shutil.rmtree(dest_static)
    shutil.copytree(STATIC, dest_static)

print('Static site generated in', OUT)
