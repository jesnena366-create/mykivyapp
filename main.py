import socket
import struct
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

PORTS = [80, 443, 22, 53, 8080, 554, 1883]
IPIFY = "http://api.ipify.org"
SPEED_URL = "http://speedtest.tele2.net/2MB.zip"


def get_public_ip():
    try:
        return urllib.request.urlopen(IPIFY, timeout=10).read().decode().strip()
    except Exception:
        return "offline"


def get_gateway():
    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if parts[1] == "00000000":
                    return socket.inet_ntoa(struct.pack("<I", int(parts[2], 16)))
    except Exception:
        pass
    return None


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()


def tcp_ping(host, port=80, timeout=2):
    start = time.time()
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return round((time.time() - start) * 1000)
    except Exception:
        return None


def host_is_up(host):
    for port in PORTS:
        if tcp_ping(host, port, timeout=1) is not None:
            return True
    return False


def hostname_of(host):
    try:
        return socket.gethostbyaddr(host)[0]
    except Exception:
        return ""


def scan_subnet():
    local = get_local_ip()
    base = ".".join(local.split(".")[:3])
    found = []
    with ThreadPoolExecutor(max_workers=60) as pool:
        futures = {pool.submit(host_is_up, f"{base}.{i}"): f"{base}.{i}" for i in range(2, 255)}
        for future in futures:
            host = futures[future]
            if future.result():
                found.append((host, hostname_of(host)))
    return sorted(found, key=lambda d: int(d[0].split(".")[3]))


def run_speed_test():
    start = time.time()
    total = 0
    try:
        with urllib.request.urlopen(SPEED_URL, timeout=15) as r:
            while time.time() - start < 10:
                chunk = r.read(65536)
                if not chunk:
                    break
                total += len(chunk)
    except Exception:
        return None
    mbps = total / (time.time() - start) / 125000
    return mbps


class ProbeApp(App):
    def build(self):
        self.device_rows = []

        tab_panel = TabbedPanel(do_default_tab=False)

        dash = TabbedPanelItem(text="Dashboard")
        self.dash_layout = BoxLayout(orientation="vertical", padding=24, spacing=16)
        self.pub_label = Label(text="Public IP: ...", font_size=20, size_hint_y=None, height=40)
        self.local_label = Label(text="Local IP: ...", font_size=20, size_hint_y=None, height=40)
        self.gw_label = Label(text="Router: ...", font_size=20, size_hint_y=None, height=40)
        self.ping_label = Label(text="Router ping: ...", font_size=24, size_hint_y=None, height=40)
        for w in (self.pub_label, self.local_label, self.gw_label, self.ping_label):
            self.dash_layout.add_widget(w)
        dash.content = self.dash_layout

        dev = TabbedPanelItem(text="Devices")
        dev_layout = BoxLayout(orientation="vertical", padding=16, spacing=12)
        scan_btn = Button(text="Scan network", size_hint_y=None, height=52)
        self.scan_status = Label(text="Not scanned yet", font_size=16, size_hint_y=None, height=32)
        dev_layout.add_widget(scan_btn)
        dev_layout.add_widget(self.scan_status)
        self.device_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8)
        self.device_box.bind(minimum_height=self.device_box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.device_box)
        dev_layout.add_widget(scroll)
        scan_btn.bind(on_press=self.start_scan)
        dev.content = dev_layout

        spd = TabbedPanelItem(text="Speed")
        spd_layout = BoxLayout(orientation="vertical", padding=24, spacing=16)
        spd_btn = Button(text="Test download speed", size_hint_y=None, height=52)
        self.speed_label = Label(text="--", font_size=28)
        spd_layout.add_widget(spd_btn)
        spd_layout.add_widget(self.speed_label)
        spd_btn.bind(on_press=self.start_speed)
        spd.content = spd_layout

        tab_panel.add_widget(dash)
        tab_panel.add_widget(dev)
        tab_panel.add_widget(spd)

        self.refresh_dashboard()
        Clock.schedule_interval(lambda dt: self.refresh_dashboard(), 5)
        return tab_panel

    def refresh_dashboard(self):
        def work():
            pub = get_public_ip()
            local = get_local_ip()
            gw = get_gateway()
            ping = tcp_ping(gw) if gw else None
            return pub, local, gw, ping

        threading.Thread(target=self._dash_worker, args=(work,), daemon=True).start()

    def _dash_worker(self, work):
        pub, local, gw, ping = work()
        Clock.schedule_once(
            lambda dt: self._set_dash(pub, local, gw, ping), 0
        )

    def _set_dash(self, pub, local, gw, ping):
        self.pub_label.text = f"Public IP: {pub}"
        self.local_label.text = f"Local IP: {local}"
        self.gw_label.text = f"Router: {gw}"
        self.ping_label.text = f"Router ping: {ping} ms" if ping else "Router ping: offline"

    def start_scan(self, instance):
        self.scan_status.text = "Scanning..."
        self.device_box.clear_widgets()
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        found = scan_subnet()
        Clock.schedule_once(lambda dt: self._show_devices(found), 0)

    def _show_devices(self, found):
        self.scan_status.text = f"{len(found)} device(s) found"
        for host, name in found:
            label = Label(
                text=f"{host}   {name if name else '?'}",
                font_size=16,
                size_hint_y=None,
                height=36,
            )
            self.device_box.add_widget(label)

    def start_speed(self, instance):
        self.speed_label.text = "Testing..."
        threading.Thread(target=self._speed_worker, daemon=True).start()

    def _speed_worker(self):
        mbps = run_speed_test()
        Clock.schedule_once(lambda dt: self._show_speed(mbps), 0)

    def _show_speed(self, mbps):
        if mbps is None:
            self.speed_label.text = "Test failed"
        else:
            self.speed_label.text = f"{mbps:.1f} Mbit/s"


if __name__ == "__main__":
    ProbeApp().run()
