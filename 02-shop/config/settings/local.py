from .base import *

if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]
    # Append last — must run after any middleware that encodes the response;
    # it injects the reload <script> before </body>.
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]
