# coding=utf-8
from __future__ import absolute_import

import ast
import os
import djcelery
from kombu import Queue
from celery.schedules import crontab
from django.conf import settings

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '8/25/16'


try:
    # import geonode settings
    from geonode.settings import *
except ImportError:
    pass

INSTALLED_APPS += (
    "geonode.qgis_server",
    "geosafe", )
INSTALLED_APPS = list(INSTALLED_APPS)

# Make priority for geosafe templates
template_dirs = list(TEMPLATES[0]['DIRS'])
template_dirs.insert(0, '/usr/src/geosafe/templates')

TEMPLATES[0]['DIRS'] = template_dirs
STATICFILES_DIRS += (
    '/usr/src/geosafe/static',
)

# QGIS Server Backend settings

# Delete Geoserver settings

try:
    INSTALLED_APPS.remove("geonode.geoserver")
    MAP_BASELAYERS.remove(LOCAL_GEOSERVER)
    del LOCAL_GEOSERVER
except:
    pass

# Leaflet config
LAYER_PREVIEW_LIBRARY = 'leaflet'
LEAFLET_CONFIG = {
    'TILES': [
        # Map Quest
        ('Map Quest',
         'http://otile4.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
         'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> '
         '&mdash; Map data &copy; '
         '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'),
    ],
    'PLUGINS': {
        'esri-leaflet': {
            'js': 'lib/js/esri-leaflet.js',
            'auto-include': True,
        },
        'leaflet-fullscreen': {
            'css': 'lib/css/leaflet.fullscreen.css',
            'js': 'lib/js/Leaflet.fullscreen.min.js',
            'auto-include': True,
        },
    },
    'SRID': 3857,
    'RESET_VIEW': False
}

# Legacy from Geoserver
# OGC_URL_INSIDE = os.environ.get('OGC_URL_INSIDE', SITEURL)
# OGC_SERVER = {
#     'default': {
#         'LOCATION': OGC_URL_INSIDE + 'qgis-server/',
#         'PUBLIC_LOCATION': SITEURL + 'qgis-server/'
#     }
# }

# OGC (WMS/WFS/WCS) Server Settings
tiles_directory = os.path.join(PROJECT_ROOT, "qgis_tiles")
QGIS_SERVER_URL = os.environ.get(
    'QGIS_SERVER_URL', 'http://qgis-server/')
QGIS_SERVER_CONFIG = {
    'tiles_directory': tiles_directory,
    'tile_path': tiles_directory + '/%s/%d/%d/%d.png',
    'legend_path': tiles_directory + '/%s/legend.png',
    'thumbnail_path': tiles_directory + '/%s/thumbnail.png',
    'map_tile_path': os.path.join(
        tiles_directory, '%s', 'map_tiles', '%s', '%s', '%s', '%s.png'),
    'qgis_server_url': QGIS_SERVER_URL,
    'layer_directory': os.path.join(PROJECT_ROOT, "qgis_layer")
}


# Geosafe settings
# App specific
# Geosafe - Celery settings

# Pick the correct broker for relaying commands to InaSAFE Headless
BROKER_URL = os.environ['BROKER_URL']
CELERY_RESULT_BACKEND = BROKER_URL

# Specific celery settings. Can be modified accordingly or leave as default
CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', False)
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_IGNORE_RESULT = False
CELERY_SEND_EVENTS = True
CELERY_TASK_RESULT_EXPIRES = 24 * 3600
CELERY_DISABLE_RATE_LIMITS = True
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"
CELERY_CREATE_MISSING_QUEUES = True
CELERYD_CONCURRENCY = 1

# Defining Celery queue to avoid clash between tasks. Leave as default
CELERY_QUEUES = [
    Queue('default', routing_key='default'),
    Queue('cleanup', routing_key='cleanup'),
    Queue('update', routing_key='update'),
    Queue('email', routing_key='email'),
    Queue('inasafe-headless', routing_key='inasafe-headless'),
    Queue('geosafe', routing_key='geosafe'),
]

# Schedule for periodic tasks
CELERYBEAT_SCHEDULE = {
    # executes every night at 0:0 AM
    'clean-impact-nightly': {
        'task': 'geosafe.tasks.analysis.clean_impact_result',
        'schedule': crontab(hour='0', minute='0')
    }
}

djcelery.setup_loader()

# base url used to resolve layer files accessed by InaSAFE Headless
GEONODE_BASE_URL = os.environ.get('GEONODE_BASE_URL', SITEURL)


# Loggers
if DEBUG:
    LOGGING["handlers"]["console"]["level"] = "DEBUG"

    LOGGING["loggers"]["geonode"] = {
        "handlers": ["console"],
        "level": "DEBUG",
    }
    LOGGING["loggers"]["geosafe"] = {
        "handlers": ["console"],
        "level": "DEBUG",
    }

if isinstance(ALLOWED_HOSTS, str):
    # convert to list
    try:
        ALLOWED_HOSTS = ast.literal_eval(ALLOWED_HOSTS)
    except:
        pass
