# Track and detect changes to modules so the app can update and so no server restard is necessary.

response.generic_patterns = ['*']
from gluon.custom_import import track_changes
track_changes(True)