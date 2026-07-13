import sys
from unittest.mock import MagicMock
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
sys.modules['gi.repository.Gtk'] = MagicMock()
sys.modules['gi.repository.GtkLayerShell'] = MagicMock()
sys.modules['gi.repository.Gst'] = MagicMock()
sys.modules['gi.repository.GLib'] = MagicMock()

try:
    import widget
    print("Widget loaded successfully with mock Gtk!")
except Exception as e:
    print(f"Failed to load widget: {e}")
    sys.exit(1)
