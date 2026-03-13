# dmg_settings.py
import urllib.parse
import os

# Volume format (see hdiutil create -help)
format = 'UDBZ'

# Volume size
size = None

# Files to include
files = [
    'dist/AverraNode.app'
]

# Symlinks to create
symlinks = {
    'Applications': '/Applications'
}

# Window configuration
window_rect = ((100, 100), (600, 400))
background = 'builtin-arrow'
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Icon positions
icon_locations = {
    'AverraNode.app': (140, 120),
    'Applications': (500, 120)
}
