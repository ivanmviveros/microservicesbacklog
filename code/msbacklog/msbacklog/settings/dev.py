from .base import *

ALLOWED_HOSTS = ['localhost','.localhost']

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# to debug_toolbar app
if 'debug_toolbar' in INSTALLED_APPS:
 
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
 
    # to debug_toolbar app
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
 
    # This example is unlikely to be appropriate for your project.
    CONFIG_DEFAULTS = {
        # Toolbar options
        'RESULTS_CACHE_SIZE': 3,
        'SHOW_COLLAPSED': True,
        # Panel options
        'SQL_WARNING_THRESHOLD': 100,   # milliseconds
    }
 
    INTERNAL_IPS = ('127.0.0.1',)