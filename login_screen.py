import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class LoginScreen(Gtk.Window):
    def __init__(self):
        super().__init__(title="Login")
        
        # Set background color via CSS

        
        self.fullscreen()
        self.set_decorated(False)
        self.set_keep_above(True)
        
        # Layout container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)
        self.add(vbox)
        
        # Label
        label = Gtk.Label(label="<span size='24000' color='#333333' weight='bold'>Sway Desktop</span>")
        label.set_use_markup(True)
        vbox.pack_start(label, False, False, 10)
        
        label_sub = Gtk.Label(label="<span size='16000' color='#555555'>Please enter your password to continue</span>")
        label_sub.set_use_markup(True)
        vbox.pack_start(label_sub, False, False, 0)
        
        # Password entry
        self.entry = Gtk.Entry()
        self.entry.set_visibility(False)
        self.entry.set_placeholder_text("Password")
        self.entry.set_alignment(0.5)
        self.entry.set_size_request(300, 50)
        
        # Styling
        css_provider = Gtk.CssProvider()
        css = b"""
        * {
            font-family: "Inter", "Ubuntu", "Fira Code", system-ui, sans-serif;
        }
        window {
            background-color: #b8d8be;
        }
        entry {
            font-size: 20px;
            padding: 10px;
            border-radius: 8px;
            background-color: #ffffff;
            color: #333333;
        }
        button {
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 8px;
            background-color: #4a8f59;
            color: white;
            font-weight: bold;
        }
        button:hover {
            background-color: #3d7a4b;
        }
        #error-label {
            font-weight: bold;
            padding: 5px;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self.entry.connect("activate", self.on_login_clicked)
        vbox.pack_start(self.entry, False, False, 10)
        
        # Error label
        self.error_label = Gtk.Label(label="")
        self.error_label.set_name("error-label")
        self.error_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.9, 0.2, 0.2, 1.0))
        vbox.pack_start(self.error_label, False, False, 0)
        
        # Login button
        button = Gtk.Button(label="Log In")
        button.set_size_request(200, 50)
        button.connect("clicked", self.on_login_clicked)
        vbox.pack_start(button, False, False, 0)
        
        self.connect("delete-event", lambda w, e: True)
        
    def on_login_clicked(self, widget):
        password = self.entry.get_text()
        if password == "148148":
            Gtk.main_quit()
        else:
            self.error_label.set_text("Incorrect password.")
            self.entry.set_text("")
            self.entry.grab_focus()

win = LoginScreen()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
