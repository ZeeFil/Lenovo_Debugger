import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell, Gst
import urllib.request
import urllib.parse
import json
import threading
import os
from datetime import datetime

# Initialize GStreamer
Gst.init(None)

class WeatherWidget(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        # Setup Layer Shell for Fullscreen Dashboard
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        
        # Transparent background for the main window (so wallpaper shows through)
        visual = self.get_screen().get_rgba_visual()
        if visual and self.get_screen().is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
        
        # Center alignment wrapper
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.add(self.center_box)

        # Dashboard Container (Glassmorphism styling)
        self.dashboard = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        self.dashboard.set_name("dashboard-container")
        self.dashboard.set_margin_top(20)
        self.dashboard.set_margin_bottom(20)
        self.dashboard.set_margin_start(30)
        self.dashboard.set_margin_end(30)
        self.center_box.pack_start(self.dashboard, False, False, 0)
        
        # Left column (Time, Date, Weather)
        self.left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.dashboard.pack_start(self.left_vbox, False, False, 0)
        
        # Clock & Date
        self.time_label = Gtk.Label()
        self.time_label.set_halign(Gtk.Align.START)
        self.date_label = Gtk.Label()
        self.date_label.set_halign(Gtk.Align.START)
        
        self.left_vbox.pack_start(self.time_label, False, False, 0)
        self.left_vbox.pack_start(self.date_label, False, False, 0)
        
        # Divider
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_name("divider")
        self.left_vbox.pack_start(separator, False, False, 10)

        # Weather box
        self.weather_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.left_vbox.pack_start(self.weather_box, False, False, 0)
        
        self.weather_labels = []
        for i in range(8):
            lbl = Gtk.Label()
            lbl.set_halign(Gtk.Align.START)
            self.weather_box.pack_start(lbl, False, False, 0)
            self.weather_labels.append(lbl)
            
        self.weather_labels[0].set_markup("<span size='14000' color='#aaddff'>Loading Weather Data...</span>")
            
        # Right column (Calendar + Radio)
        self.right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.right_vbox.set_valign(Gtk.Align.CENTER)
        self.dashboard.pack_start(self.right_vbox, False, False, 0)
        
        self.calendar = Gtk.Calendar()
        self.right_vbox.pack_start(self.calendar, False, False, 0)
        
        # --- RADIO WIDGET ---
        self.radio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.radio_box.set_name("radio-container")
        self.right_vbox.pack_start(self.radio_box, False, False, 0)
        
        self.station_label = Gtk.Label()
        self.station_label.set_halign(Gtk.Align.CENTER)
        self.radio_box.pack_start(self.station_label, False, False, 0)
        
        self.now_playing_label = Gtk.Label()
        self.now_playing_label.set_halign(Gtk.Align.CENTER)
        self.now_playing_label.set_line_wrap(True)
        self.now_playing_label.set_max_width_chars(30)
        self.radio_box.pack_start(self.now_playing_label, False, False, 0)
        
        self.radio_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.radio_controls.set_halign(Gtk.Align.CENTER)
        self.radio_box.pack_start(self.radio_controls, False, False, 0)
        
        self.btn_prev = Gtk.Button(label="⏮")
        self.btn_play = Gtk.Button(label="▶")
        self.btn_next = Gtk.Button(label="⏭")
        
        self.btn_prev.connect("clicked", self.on_radio_prev)
        self.btn_play.connect("clicked", self.on_radio_play_toggle)
        self.btn_next.connect("clicked", self.on_radio_next)
        
        for btn in [self.btn_prev, self.btn_play, self.btn_next]:
            btn.get_style_context().add_class("radio-btn")
            self.radio_controls.pack_start(btn, False, False, 0)
            
        # Volume Control
        self.volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.volume_box.set_halign(Gtk.Align.CENTER)
        self.radio_box.pack_start(self.volume_box, False, False, 0)
        
        vol_icon = Gtk.Label(label="🔊")
        self.volume_box.pack_start(vol_icon, False, False, 0)
        
        self.volume_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_slider.set_value(100)
        self.volume_slider.set_size_request(150, -1)
        self.volume_slider.set_draw_value(False)
        self.volume_slider.connect("value-changed", self.on_volume_changed)
        self.volume_box.pack_start(self.volume_slider, False, False, 0)

        # Radio State and Backend
        self.stations = [
            {"name": "ABC Triple J", "url": "https://mediaserviceslive.akamaized.net/hls/live/2038347/triplejqld/masterhq.m3u8"},
            {"name": "Double J", "url": "https://mediaserviceslive.akamaized.net/hls/live/2038342/doublejqld/index.m3u8"},
            {"name": "ABC Radio Sydney", "url": "https://mediaserviceslive.akamaized.net/hls/live/2038302/localsydney/masterhq.m3u8"},
            {"name": "Smooth FM", "url": "http://playerservices.streamtheworld.com/api/livestream-redirect/SMOOTH953_AAC320.aac"},
            {"name": "Triple M", "url": "https://wz4liw.scahw.com.au/live/4mmm_128.stream/playlist.m3u8"},
            {"name": "Gold 104.3", "url": "https://ais-arn.streamguys1.com/au_004_icy"},
            {"name": "2GB Sydney", "url": "http://playerservices.streamtheworld.com/api/livestream-redirect/2GB.mp3"},
            {"name": "BBC Radio 1", "url": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"},
            {"name": "KEXP Seattle", "url": "https://kexp.streamguys1.com/kexp160.aac"},
            {"name": "FIP Paris", "url": "http://icecast.radiofrance.fr/fip-midfi.mp3"}
        ]
        self.current_station_idx = 0
        self.is_playing = False
        
        self.player = Gst.ElementFactory.make("playbin", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_gst_message)

        # Initialize labels for radio
        self.update_station_ui()
            
        # CSS Styling
        css = b"""
        window {
            background-color: transparent;
        }
        #dashboard-container {
            background-color: rgba(15, 15, 20, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 30px;
        }
        * {
            font-family: "Inter", "Ubuntu", "Fira Code", system-ui, sans-serif;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }
        #divider {
            background-color: rgba(255, 255, 255, 0.1);
            min-height: 1px;
        }
        calendar {
            background-color: transparent;
            color: white;
            font-size: 16px;
        }
        calendar.header {
            background-color: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            font-weight: bold;
            padding-bottom: 8px;
        }
        calendar.button {
            color: rgba(255, 255, 255, 0.7);
        }
        calendar.button:hover {
            color: white;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
        }
        calendar:selected {
            background-color: rgba(100, 150, 255, 0.5);
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
        
        /* Radio Styles */
        #radio-container {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 15px;
            margin-top: 10px;
        }
        .radio-btn {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 10px;
            border: none;
            padding: 10px 15px;
            font-size: 18px;
        }
        .radio-btn:hover {
            background-color: rgba(255, 255, 255, 0.25);
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Start timers
        self.update_time()
        GLib.timeout_add_seconds(1, self.update_time)
        
        # Fetch weather in background
        self.fetch_weather_thread()
        GLib.timeout_add_seconds(1800, self.fetch_weather_thread)

    def update_station_ui(self):
        station = self.stations[self.current_station_idx]
        self.station_label.set_markup(f"<span size='16000' weight='bold' color='white'>📻 {station['name']}</span>")
        if not self.is_playing:
            self.now_playing_label.set_markup("<span size='12000' color='#aaddff'>Press play to listen</span>")
            self.btn_play.set_label("▶")

    def on_radio_play_toggle(self, widget):
        if self.is_playing:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False
            self.update_station_ui()
        else:
            self.play_current_station()
            
    def play_current_station(self):
        self.player.set_state(Gst.State.NULL)
        station = self.stations[self.current_station_idx]
        self.player.set_property("uri", station["url"])
        self.player.set_state(Gst.State.PLAYING)
        self.is_playing = True
        self.btn_play.set_label("⏸")
        self.station_label.set_markup(f"<span size='16000' weight='bold' color='#66ff99'>📻 {station['name']}</span>")
        self.now_playing_label.set_markup("<span size='12000' color='#aaddff'>Connecting...</span>")
        
    def on_radio_prev(self, widget):
        self.current_station_idx = (self.current_station_idx - 1) % len(self.stations)
        if self.is_playing:
            self.play_current_station()
        else:
            self.update_station_ui()
            
    def on_radio_next(self, widget):
        self.current_station_idx = (self.current_station_idx + 1) % len(self.stations)
        if self.is_playing:
            self.play_current_station()
        else:
            self.update_station_ui()

    def on_volume_changed(self, widget):
        val = widget.get_value() / 100.0
        self.player.set_property("volume", val)

    def on_gst_message(self, bus, message):
        if message.type == Gst.MessageType.TAG:
            tags = message.parse_tag()
            title = ""
            artist = ""
            
            has_title, title = tags.get_string(Gst.TAG_TITLE)
            has_artist, artist = tags.get_string(Gst.TAG_ARTIST)
            
            display_text = ""
            if has_title and title:
                display_text = title
            if has_artist and artist:
                display_text = f"{artist} - {display_text}"
                
            if display_text:
                GLib.idle_add(self.update_now_playing, display_text)
                
    def update_now_playing(self, text):
        text = text.replace("&", "&amp;").replace("<", "&lt;")
        self.now_playing_label.set_markup(f"<span size='12000' color='#aaddff'><i>{text}</i></span>")

    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%A, %B %d")
        self.time_label.set_markup(f"<span size='64000' weight='800' color='white'>{time_str}</span>")
        self.date_label.set_markup(f"<span size='20000' weight='300' color='#dddddd'>{date_str}</span>")
        self.calendar.select_month(now.month - 1, now.year)
        self.calendar.select_day(now.day)
        return True

    def fetch_weather_thread(self):
        thread = threading.Thread(target=self.fetch_weather)
        thread.daemon = True
        thread.start()
        return True

    def fetch_weather(self):
        try:
            # 1. Get Location
            lat = -33.8688
            lon = 151.2093
            city = "Sydney"
            
            # Check for config file
            config_file = os.path.expanduser("~/.config/weather_location.txt")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    city_query = f.read().strip()
                if city_query:
                    # Geocode the city using Open-Meteo Geocoding API
                    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city_query)}&count=1&language=en&format=json"
                    req_geo = urllib.request.Request(geo_url, headers={'User-Agent': 'Mozilla/5.0'})
                    try:
                        with urllib.request.urlopen(req_geo, timeout=5) as response:
                            geo_data = json.loads(response.read().decode())
                            if geo_data.get("results"):
                                result = geo_data["results"][0]
                                lat = result.get("latitude", lat)
                                lon = result.get("longitude", lon)
                                city = result.get("name", city_query)
                    except Exception:
                        pass
            
            if city == "Sydney":
                # Fallback to IP API
                try:
                    req = urllib.request.Request("http://ip-api.com/json", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        loc_data = json.loads(response.read().decode())
                        lat = loc_data.get('lat', lat)
                        lon = loc_data.get('lon', lon)
                        city = loc_data.get('city', city)
                except Exception:
                    pass
            
            # 2. Get Weather (7 days)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
            req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=5) as response:
                w_data = json.loads(response.read().decode())
                
            daily = w_data.get('daily', {})
            times = daily.get('time', [])
            max_temps = daily.get('temperature_2m_max', [])
            min_temps = daily.get('temperature_2m_min', [])
            codes = daily.get('weathercode', [])
            
            GLib.idle_add(self.update_weather_ui, city, times, max_temps, min_temps, codes)
            
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))

    def update_weather_ui(self, city, times, max_temps, min_temps, codes):
        def get_icon(code):
            if code == 0: return "☀️"
            if code in [1, 2, 3]: return "⛅"
            if code in [45, 48]: return "🌫️"
            if code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67]: return "🌧️"
            if code in [71, 73, 75, 77, 85, 86]: return "❄️"
            if code in [80, 81, 82]: return "🌦️"
            if code in [95, 96, 99]: return "⛈️"
            return "🌥️"

        if len(self.weather_labels) > 0:
            self.weather_labels[0].set_markup(f"<span size='14000' weight='bold' color='#aaddff'>📍 {city}</span>")
            
        for i in range(1, 8):
            if i-1 < len(times) and i-1 < len(max_temps) and i-1 < len(min_temps) and i-1 < len(codes):
                date_obj = datetime.strptime(times[i-1], "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                if i == 1: day_name = "Today"
                
                icon = get_icon(codes[i-1])
                tmax = round(max_temps[i-1])
                tmin = round(min_temps[i-1])
                
                markup = f"<span size='13000' color='white' font_family='monospace'>{icon}  {tmin:2d}° / {tmax:2d}°   {day_name}</span>"
                self.weather_labels[i].set_markup(markup)
        return False

    def show_error(self, err):
        for lbl in self.weather_labels:
            lbl.set_text("")
        if len(self.weather_labels) > 0:
            self.weather_labels[0].set_markup(f"<span color='red'>Weather Error: Unable to fetch data</span>")
        return False

win = WeatherWidget()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
