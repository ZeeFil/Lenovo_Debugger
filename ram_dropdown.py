import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess

GLib.set_prgname('ram_dropdown')

CSS = b"""
window {
    font-family: "Inter", "Ubuntu", "Fira Code", system-ui, sans-serif, FontAwesome;
    background-color: rgba(30, 30, 46, 0.95);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
label#header {
    font-size: 22px;
    font-weight: bold;
    color: #cad3f5;
    margin-bottom: 5px;
}
label#subheader {
    font-size: 15px;
    font-weight: bold;
    color: #8aadf4;
    margin-top: 15px;
}
label#value {
    font-size: 14px;
    color: #a6da95;
    margin-bottom: 5px;
}
progressbar trough {
    min-height: 14px;
    border-radius: 7px;
    background-color: rgba(255, 255, 255, 0.15);
}
progressbar progress {
    background-color: #f5a97f;
    border-radius: 7px;
}
progressbar#disk progress {
    background-color: #8bd5ca;
}
progressbar#swap progress {
    background-color: #cba6f7;
}
"""

class SpecsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="ram_dropdown")
        self.set_wmclass("ram_dropdown", "ram_dropdown")
        self.set_decorated(False)
        self.set_default_size(640, 520)
        
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)
        
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.set_margin_top(25)
        main_box.set_margin_bottom(25)
        main_box.set_margin_start(30)
        main_box.set_margin_end(30)
        self.add(main_box)
        
        header = Gtk.Label()
        header.set_markup("<span font_desc='FontAwesome 16'></span>  Live Device Specifications")
        header.set_name("header")
        header.set_halign(Gtk.Align.START)
        main_box.pack_start(header, False, False, 0)
        
        # CPU
        cpu_lbl = Gtk.Label()
        cpu_lbl.set_markup("<span font_desc='FontAwesome 12'></span>  System Kernel:")
        cpu_lbl.set_name("subheader")
        cpu_lbl.set_halign(Gtk.Align.START)
        main_box.pack_start(cpu_lbl, False, False, 0)
        
        self.cpu_val = Gtk.Label()
        self.cpu_val.set_name("value")
        self.cpu_val.set_halign(Gtk.Align.START)
        self.cpu_val.set_line_wrap(True)
        main_box.pack_start(self.cpu_val, False, False, 0)
        
        # RAM
        ram_lbl = Gtk.Label()
        ram_lbl.set_markup("<span font_desc='FontAwesome 12'></span>  Physical Memory:")
        ram_lbl.set_name("subheader")
        ram_lbl.set_halign(Gtk.Align.START)
        main_box.pack_start(ram_lbl, False, False, 0)
        
        self.ram_val = Gtk.Label()
        self.ram_val.set_name("value")
        self.ram_val.set_halign(Gtk.Align.START)
        main_box.pack_start(self.ram_val, False, False, 0)
        
        self.progress = Gtk.ProgressBar()
        main_box.pack_start(self.progress, False, False, 5)

        # SWAP / ZRAM
        swap_lbl = Gtk.Label()
        swap_lbl.set_markup("<span font_desc='FontAwesome 12'></span>  ZRAM / Swap:")
        swap_lbl.set_name("subheader")
        swap_lbl.set_halign(Gtk.Align.START)
        main_box.pack_start(swap_lbl, False, False, 0)
        
        self.swap_val = Gtk.Label()
        self.swap_val.set_name("value")
        self.swap_val.set_halign(Gtk.Align.START)
        main_box.pack_start(self.swap_val, False, False, 0)
        
        self.swap_progress = Gtk.ProgressBar()
        self.swap_progress.set_name("swap")
        main_box.pack_start(self.swap_progress, False, False, 5)
        
        # Disk
        disk_lbl = Gtk.Label()
        disk_lbl.set_markup("<span font_desc='FontAwesome 12'></span>  Internal Storage ( / ):")
        disk_lbl.set_name("subheader")
        disk_lbl.set_halign(Gtk.Align.START)
        main_box.pack_start(disk_lbl, False, False, 0)
        
        self.disk_val = Gtk.Label()
        self.disk_val.set_name("value")
        self.disk_val.set_halign(Gtk.Align.START)
        main_box.pack_start(self.disk_val, False, False, 0)
        
        self.disk_progress = Gtk.ProgressBar()
        self.disk_progress.set_name("disk")
        main_box.pack_start(self.disk_progress, False, False, 5)
        
        self.update_specs()
        GLib.timeout_add_seconds(2, self.update_specs)
        
    def update_specs(self):
        try:
            uptime = subprocess.check_output("uptime", shell=True).decode('utf-8').strip()
            # uptime usually looks like:  14:35:01 up 17:36,  1 user,  load average: 0.14, 0.20, 0.18
            uptime_parts = uptime.split("load average:")
            up_str = uptime_parts[0].replace("  ", " ").strip()
            load_str = uptime_parts[1].strip() if len(uptime_parts) > 1 else ""
            
            uname = subprocess.check_output("uname -r", shell=True).decode('utf-8').strip()
            self.cpu_val.set_markup(f"<b>Kernel:</b> {uname}\n<b>Uptime:</b> {up_str}\n<b>Load Avg:</b> {load_str}")
            
            free = subprocess.check_output("free -m", shell=True).decode('utf-8').strip().split('\n')
            
            # RAM
            mem_line = free[1].split()
            total = float(mem_line[1])
            used = float(mem_line[2])
            available = float(mem_line[6])  # 'available' is the 7th column in free output
            
            frac = used / total if total > 0 else 0
            self.progress.set_fraction(frac)
            
            pct = int(frac * 100)
            self.ram_val.set_text(f"{pct}% Used  ({used/1024:.1f} GB / {total/1024:.1f} GB)  -  {available/1024:.1f} GB Available")
            
            # SWAP
            if len(free) > 2:
                swap_line = free[2].split()
                s_total = float(swap_line[1])
                s_used = float(swap_line[2])
                s_free = float(swap_line[3])
                
                s_frac = s_used / s_total if s_total > 0 else 0
                self.swap_progress.set_fraction(s_frac)
                
                s_pct = int(s_frac * 100)
                if s_total > 0:
                    self.swap_val.set_text(f"{s_pct}% Used  ({s_used/1024:.2f} GB / {s_total/1024:.1f} GB)  -  {s_free/1024:.1f} GB Free")
                else:
                    self.swap_val.set_text("0% Used  (0.0 GB / 0.0 GB)")
            
            # Disk
            df = subprocess.check_output("df -h /", shell=True).decode('utf-8').strip().split('\n')
            if len(df) > 1:
                # df output can sometimes split across lines for very long mount names.
                # The actual sizes are always on the last line.
                disk_parts = df[-1].split()
                if len(disk_parts) >= 5:
                    d_total = disk_parts[-5]
                    d_used = disk_parts[-4]
                    d_avail = disk_parts[-3]
                    d_pct_str = disk_parts[-2].replace('%', '')
                    
                    self.disk_val.set_text(f"{d_pct_str}% Used  ({d_used} / {d_total})  -  {d_avail} Available")
                    self.disk_progress.set_fraction(float(d_pct_str) / 100.0)
                
        except Exception as e:
            self.cpu_val.set_text(f"Error loading stats: {e}")
        return True

    def on_focus_out(self, widget, event):
        Gtk.main_quit()
        
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

win = SpecsWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
