# coding=utf-8
import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'


def update_settings(settings):
    """Update settings file for qgis server."""

    # Settings for QGIS Server

    settings.GEONODE_APPS += ("geonode.qgis_server", )
    settings.GEONODE_APPS = list(settings.GEONODE_APPS)
    settings.INSTALLED_APPS += (
        "geonode.qgis_server", )
    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)

    # Delete Geoserver settings

    try:
        settings.INSTALLED_APPS.remove("geonode.geoserver")
        settings.GEONODE_APPS.remove("geonode.geoserver")
        settings.MAP_BASELAYERS.remove(settings.LOCAL_GEOSERVER)
        del settings.LOCAL_GEOSERVER

        geoserver_context_processor = 'geonode.geoserver.context_processors.geoserver_urls'
        settings.TEMPLATES[0]['OPTIONS']['context_processors'].remove(geoserver_context_processor)

        qgis_server_context_processor = 'geonode.qgis_server.context_processors.qgis_server_urls'
        settings.TEMPLATES[0]['OPTIONS']['context_processors'].append(qgis_server_context_processor)
    except:
        pass

    # Leaflet config
    settings.LAYER_PREVIEW_LIBRARY = 'leaflet'
    if not hasattr(settings, 'LEAFLET_CONFIG'):
        settings.LEAFLET_CONFIG = {
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

    # QGIS Server as local OGC Server, wrapped by geonode itself.
    settings.OGC_URL_INSIDE = os.environ.get('OGC_URL_INSIDE', settings.SITEURL)
    settings.OGC_SERVER = {
        'default': {
            'BACKEND': 'geonode.qgis_server',
            'LOCATION': settings.OGC_URL_INSIDE + 'qgis-server/',
            'PUBLIC_LOCATION': settings.SITEURL + 'qgis-server/'
        }
    }

    # OGC (WMS/WFS/WCS) Server Settings
    tiles_directory = os.path.join(settings.PROJECT_ROOT, "qgis_tiles")
    layer_directory = os.path.join(settings.PROJECT_ROOT, "qgis_layer")
    settings.QGIS_SERVER_URL = os.environ.get(
        'QGIS_SERVER_URL', 'http://qgis-server/')
    settings.QGIS_SERVER_CONFIG = {
        'tiles_directory': tiles_directory,
        'tile_path': tiles_directory + '/%s/%s/%d/%d/%d.png',
        'legend_path': tiles_directory + '/%s/%s/legend.png',
        'thumbnail_path': tiles_directory + '/%s/thumbnail.png',
        'map_tile_path': os.path.join(
            tiles_directory, '%s', 'map_tiles', '%s', '%s', '%s', '%s.png'),
        'qgis_server_url': settings.QGIS_SERVER_URL,
        'layer_directory': layer_directory
    }

    # Middleware classes
    settings.MIDDLEWARE_CLASSES += (
        'geonode.qgis_server.middleware.QGISServerLayerMiddleware',
    )
