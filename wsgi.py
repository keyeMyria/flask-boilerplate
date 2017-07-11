from application import create_app
from werkzeug.contrib.fixers import ProxyFix

app = ProxyFix(create_app())
