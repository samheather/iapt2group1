# Track and detect changes to modules so the app can update.

response.generic_patterns = ['*']
from gluon.custom_import import track_changes
track_changes(True)