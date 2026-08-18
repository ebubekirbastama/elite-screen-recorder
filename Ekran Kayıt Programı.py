"""
Elite Screen Recorder
======================
Modern, hafif ve çapraz platform (Windows / Linux / macOS) ekran kayıt uygulaması.

Öne çıkan özellikler:
- CustomTkinter ile modern, koyu temalı, efektli (hover/glow) arayüz
- 720p / 1080p / 1440p / 4K / 8K çözünürlük seçenekleri
- Ayarlanabilir FPS (15 / 24 / 30 / 60)
- Mikrofon ve/veya sistem sesi kaydı
- Video/ses işini FFmpeg'e devrederek düşük CPU/RAM kullanımı
- Çıktı klasörünü otomatik oluşturma (Belgeler/EliteScreenRecorder/Kayitlar)
- Windows'ta arka planda çalışırken siyah CMD penceresi göstermez
- Kayıt süresi sayaç, durum etiketi ve şık başlat/durdur butonu

Gereksinimler (requirements.txt içinde de var):
    pip install customtkinter pillow sounddevice

Ayrıca sisteminizde FFmpeg kurulu ve PATH'e ekli olmalı:
    Windows : https://www.gyan.dev/ffmpeg/builds/  (zip indirip PATH'e ekleyin)
    macOS   : brew install ffmpeg
    Linux   : sudo apt install ffmpeg   (veya dağıtımınıza uygun paket yöneticisi)
"""

import os
import sys
import time
import shutil
import platform
import subprocess
import threading
import re
from datetime import datetime
from pathlib import Path

# Windows: uygulama GUI modunda çalışsın; mevcut konsol penceresini gizle.
# En temiz dağıtım yöntemi yine .pyw veya PyInstaller --noconsole kullanmaktır.
if platform.system() == "Windows":
    try:
        import ctypes
        _console = ctypes.windll.kernel32.GetConsoleWindow()
        if _console:
            ctypes.windll.user32.ShowWindow(_console, 0)  # SW_HIDE
    except Exception:
        pass



# --------------------------------------------------------------------------- #
#  Başlangıç kontrolü: eksik paketleri / FFmpeg'i otomatik kurar
# --------------------------------------------------------------------------- #

SYSTEM_EARLY = platform.system()
REQUIRED_PACKAGES = {
    "customtkinter": "customtkinter",
    "sounddevice": "sounddevice",
    "PIL": "pillow",
}


def _hidden_kwargs_early():
    kwargs = {}
    if SYSTEM_EARLY == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        kwargs["startupinfo"] = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def _pip_install(package: str) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", package],
            **_hidden_kwargs_early(),
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_python_packages():
    """Eksik Python paketlerini otomatik olarak kurar. Konsolsuz (.exe) modda da
    çalışsın diye herhangi bir kullanıcı girdisi beklemez."""
    import importlib

    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return

    print(f"Eksik paketler tespit edildi, kuruluyor: {', '.join(missing)}")
    for pip_name in missing:
        _pip_install(pip_name)

    # Kurulumdan sonra tekrar dene; hâlâ eksikse kullanıcıyı bilgilendir ve çık
    still_missing = []
    importlib.invalidate_caches()
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            still_missing.append(pip_name)

    if still_missing:
        msg = (
            "Aşağıdaki paketler otomatik kurulamadı, lütfen elle kurun:\n\n"
            f"pip install {' '.join(still_missing)}"
        )
        try:
            import tkinter
            from tkinter import messagebox
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Elite Screen Recorder - Kurulum", msg)
        except Exception:
            print(msg)
        sys.exit(1)


FFMPEG_PATH = r"C:\\ffmpeg.exe"


def find_ffmpeg() -> str | None:
    """Önce C:\\ffmpeg.exe yolunu, sonra sistem PATH'ini kontrol eder."""
    if os.path.isfile(FFMPEG_PATH):
        return FFMPEG_PATH
    return shutil.which("ffmpeg")


def _try_install_ffmpeg() -> bool:
    """İşletim sistemine göre FFmpeg'i otomatik kurmayı dener.
    Windows: winget (Win10 2004+ / Win11'de hazır gelir)
    macOS: Homebrew (kuruluysa)
    Linux: apt (Debian/Ubuntu tabanlı dağıtımlarda)
    Hiçbiri uygun değilse False döner ve kullanıcıya elle kurulum önerilir."""
    try:
        if SYSTEM_EARLY == "Windows" and shutil.which("winget"):
            subprocess.run(
                ["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                 "--accept-package-agreements", "--accept-source-agreements"],
                **_hidden_kwargs_early(),
            )
            return shutil.which("ffmpeg") is not None

        elif SYSTEM_EARLY == "Darwin" and shutil.which("brew"):
            subprocess.run(["brew", "install", "ffmpeg"])
            return shutil.which("ffmpeg") is not None

        elif SYSTEM_EARLY == "Linux" and shutil.which("apt"):
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"])
            return shutil.which("ffmpeg") is not None

    except Exception:
        pass
    return False


def ensure_ffmpeg():
    """FFmpeg kurulu değilse otomatik kurmayı dener; olmazsa kullanıcıyı
    indirme sayfasına yönlendiren bir uyarı gösterir (uygulamayı kapatmaz,
    kayıt başlatılınca zaten tekrar uyarılır)."""
    if find_ffmpeg():
        return

    print("FFmpeg bulunamadı, otomatik kurulum deneniyor...")
    installed = _try_install_ffmpeg()

    if not installed:
        msg = (
            "FFmpeg otomatik kurulamadı.\n\n"
            "Lütfen elle kurun:\n"
            "  Windows : winget install Gyan.FFmpeg  (veya gyan.dev'den indirin)\n"
            "  macOS   : brew install ffmpeg\n"
            "  Linux   : sudo apt install ffmpeg\n\n"
            "Kurduktan sonra programı yeniden başlatın."
        )
        try:
            import tkinter
            from tkinter import messagebox
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showwarning("Elite Screen Recorder - FFmpeg", msg)
            root.destroy()
        except Exception:
            print(msg)


ensure_python_packages()
ensure_ffmpeg()

import customtkinter as ctk
from tkinter import messagebox

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except Exception:
    HAS_SOUNDDEVICE = False


# --------------------------------------------------------------------------- #
#  Genel ayarlar / sabitler
# --------------------------------------------------------------------------- #

APP_NAME = "Elite Screen Recorder"
ACCENT = "#7C4DFF"          # ana vurgu rengi (mor)
ACCENT_HOVER = "#9E7BFF"
ACCENT_DANGER = "#FF4D6D"
ACCENT_DANGER_HOVER = "#FF7A93"
BG_DARK = "#0F0F14"
CARD_BG = "#17171F"

RESOLUTIONS = {
    "720p (HD)": (1280, 720),
    "1080p (Full HD)": (1920, 1080),
    "1440p (2K)": (2560, 1440),
    "2160p (4K)": (3840, 2160),
    "4320p (8K)": (7680, 4320),
}

FPS_OPTIONS = ["15", "24", "30", "60"]

SYSTEM = SYSTEM_EARLY  # aynı platform bilgisini yeniden kullan


def list_monitors():
    """Windows'ta bağlı ekranları listeler.
    Dönüş: [(etiket, x, y, width, height), ...]
    """
    monitors = []
    if SYSTEM != "Windows":
        return [("Ana Ekran", 0, 0, 0, 0)]

    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            wintypes.HMONITOR,
            wintypes.HDC,
            ctypes.POINTER(wintypes.RECT),
            wintypes.LPARAM,
        )

        def _callback(hmonitor, hdc, rect_ptr, lparam):
            r = rect_ptr.contents
            x, y = r.left, r.top
            w, h = r.right - r.left, r.bottom - r.top
            monitors.append((f"Ekran {len(monitors)+1} ({w}x{h})", x, y, w, h))
            return 1

        user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(_callback), 0)
    except Exception:
        pass

    return monitors or [("Tüm Masaüstü", 0, 0, 0, 0)]


def list_windows():
    """Windows'ta görünür, başlığı olan pencereleri listeler."""
    if SYSTEM != "Windows":
        return []

    titles = []
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

        def callback(hwnd, lparam):
            if not user32.IsWindowVisible(hwnd):
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True

            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.strip()

            if title and title != APP_NAME:
                titles.append(title)
            return True

        user32.EnumWindows(EnumWindowsProc(callback), 0)
    except Exception:
        pass

    # Aynı başlıklardan tekrarları kaldır.
    seen = set()
    unique = []
    for title in titles:
        if title not in seen:
            seen.add(title)
            unique.append(title)
    return unique


def ensure_admin_on_windows():
    """Windows'ta program yönetici (admin) yetkisiyle çalışmıyorsa,
    UAC onayı isteyip kendini yönetici olarak yeniden başlatır."""
    if SYSTEM != "Windows":
        return
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        import ctypes
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{a}"' for a in sys.argv[1:]])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
        except Exception:
            pass
        sys.exit(0)


def _windows_videos_folder() -> Path | None:
    """Windows'ta gerçek 'Videos' klasör yolunu Registry/Shell API üzerinden bulur.
    Bazı sistemlerde bu klasör OneDrive'a veya farklı bir sürücüye taşınmış olabilir,
    bu yüzden sabit 'home / Videos' varsayımı her zaman doğru olmayabilir."""
    try:
        import ctypes
        from ctypes import wintypes

        CSIDL_MYVIDEO = 0x000E
        SHGFP_TYPE_CURRENT = 0

        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_MYVIDEO, 0, SHGFP_TYPE_CURRENT, buf)
        path = Path(buf.value)
        if path and str(path):
            return path
    except Exception:
        pass
    return None


def get_output_dir() -> Path:
    """Çıktı klasörünü bulur/oluşturur. Birden çok aday yol dener; hiçbiri
    çalışmazsa kullanıcı klasörü altına (her zaman var olan bir konuma) düşer,
    böylece uygulama asla klasör bulunamadığı için çökmez."""
    home = Path.home()
    candidates = []

    if SYSTEM == "Windows":
        win_videos = _windows_videos_folder()
        if win_videos:
            candidates.append(win_videos)
        candidates.append(home / "Videos")
        candidates.append(Path(os.environ.get("USERPROFILE", str(home))) / "Videos")
    elif SYSTEM == "Darwin":
        candidates.append(home / "Movies")
    else:
        candidates.append(home / "Videos")

    # Her ihtimale karşı son çare: kullanıcı klasörünün doğrudan altı
    candidates.append(home)

    last_error = None
    for base in candidates:
        try:
            out_dir = Path(base) / "EliteScreenRecorder" / "Kayitlar"
            out_dir.mkdir(parents=True, exist_ok=True)
            return out_dir
        except Exception as e:
            last_error = e
            continue

    # Buraya hiç düşmemeli, ama garanti olsun diye:
    raise RuntimeError(f"Çıktı klasörü hiçbir konumda oluşturulamadı: {last_error}")



def hidden_subprocess_kwargs():
    """Windows'ta ffmpeg'i konsol penceresi açmadan çalıştırmak için gerekli ayarlar."""
    kwargs = {}
    if SYSTEM == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        kwargs["startupinfo"] = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def list_microphones():
    """Mikrofonları kayıt motoruyla aynı kaynaktan listeler.

    Windows'ta doğrudan FFmpeg DirectShow (dshow) cihaz adları kullanılır.
    Böylece sounddevice ile FFmpeg arasındaki cihaz adı uyuşmazlığı önlenir.
    """
    devices = ["Yok"]

    if SYSTEM == "Windows":
        ffmpeg = find_ffmpeg()
        if ffmpeg:
            try:
                result = subprocess.run(
                    [
                        ffmpeg,
                        "-hide_banner",
                        "-list_devices", "true",
                        "-f", "dshow",
                        "-i", "dummy",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=8,
                    **hidden_subprocess_kwargs(),
                )

                output = result.stderr or ""
                in_audio_section = False

                for line in output.splitlines():
                    low = line.lower()

                    if "directshow audio devices" in low:
                        in_audio_section = True
                        continue

                    if "directshow video devices" in low:
                        in_audio_section = False
                        continue

                    if not in_audio_section:
                        continue

                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        name = match.group(1).strip()

                        # FFmpeg bazı cihazlar için ayrıca alternatif @device_...
                        # satırı yazar; kullanıcıya sadece okunabilir gerçek adı göster.
                        if (
                            name
                            and not name.startswith("@device_")
                            and name not in devices
                        ):
                            devices.append(name)

                if len(devices) > 1:
                    return devices

            except Exception:
                pass

    # Windows dışında veya FFmpeg listeleme başarısızsa yedek yöntem.
    if HAS_SOUNDDEVICE:
        try:
            for d in sd.query_devices():
                if d.get("max_input_channels", 0) > 0:
                    name = str(d["name"]).strip()
                    if name and name not in devices:
                        devices.append(name)
        except Exception:
            pass

    return devices


# --------------------------------------------------------------------------- #
#  Kayıt motoru (FFmpeg ile) - düşük sistem yükü için native encoder katmanı
# --------------------------------------------------------------------------- #

class Recorder:
    def __init__(self):
        self.process = None
        self.output_file = None
        self.start_time = None
        self.log_file = None
        self._log_handle = None

    def _pick_encoder(self):
        """Kararlı kayıt için libx264 kullanır.
        FFmpeg bazı donanım encoderlarını listelese bile ilgili GPU/driver
        mevcut olmayabilir; bu durumda kayıt işlemi anında kapanabilir.
        """
        return "libx264"

    def build_command(self, width, height, fps, mic_device, system_audio, out_path, source_mode="Ekran", monitor_info=None, window_title=None):
        ffmpeg = find_ffmpeg()
        cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]

        # ------- Video girişi -------
        if SYSTEM == "Windows":
            if source_mode == "Pencere":
                if not window_title:
                    raise RuntimeError("Kayıt için bir pencere seçmelisiniz.")
                cmd += [
                    "-f", "gdigrab",
                    "-framerate", fps,
                    "-draw_mouse", "1",
                    "-thread_queue_size", "1024",
                    "-i", f"title={window_title}"
                ]
            else:
                # Belirli monitörü masaüstü koordinatlarıyla yakala.
                if monitor_info:
                    _, offset_x, offset_y, mon_w, mon_h = monitor_info
                    cmd += [
                        "-f", "gdigrab",
                        "-framerate", fps,
                        "-draw_mouse", "1",
                        "-thread_queue_size", "1024",
                        "-offset_x", str(offset_x),
                        "-offset_y", str(offset_y),
                        "-video_size", f"{mon_w}x{mon_h}",
                        "-i", "desktop"
                    ]
                else:
                    cmd += [
                        "-f", "gdigrab",
                        "-framerate", fps,
                        "-draw_mouse", "1",
                        "-thread_queue_size", "1024",
                        "-i", "desktop"
                    ]
        elif SYSTEM == "Darwin":
            # avfoundation hem video hem sesi tek girişte verebilir; video index genelde 1 (ekran)
            cmd += ["-f", "avfoundation", "-framerate", fps, "-i", "1:none"]
        else:  # Linux
            display = os.environ.get("DISPLAY", ":0.0")
            cmd += ["-f", "x11grab", "-framerate", fps, "-i", display]

        # ------- Ses girişleri -------
        audio_inputs = 0
        if mic_device and mic_device != "Yok":
            if SYSTEM == "Windows":
                cmd += [
                    "-thread_queue_size", "1024",
                    "-f", "dshow",
                    "-i", f"audio={mic_device}"
                ]
            elif SYSTEM == "Darwin":
                cmd += ["-f", "avfoundation", "-i", f":{mic_device}"]
            else:
                cmd += ["-f", "pulse", "-i", mic_device]
            audio_inputs += 1

        if system_audio:
            if SYSTEM == "Windows":
                # "Stereo Mix" cihazı etkinse sistem sesini de dshow üzerinden alır
                cmd += ["-f", "dshow", "-i", "audio=Stereo Mix"]
            elif SYSTEM == "Linux":
                cmd += ["-f", "pulse", "-i", "default"]
            # macOS için sistem sesi genelde ek sanal cihaz (BlackHole vb.) gerektirir
            audio_inputs += 1

        # ------- Video filtreleri / ölçekleme -------
        cmd += ["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"]

        # ------- Encoder ayarları (düşük yük) -------
        encoder = self._pick_encoder()
        cmd += ["-c:v", encoder]
        if encoder == "libx264":
            cmd += ["-preset", "ultrafast", "-crf", "23", "-tune", "zerolatency"]
        cmd += ["-pix_fmt", "yuv420p"]

        if audio_inputs > 0:
            cmd += ["-c:a", "aac", "-b:a", "160k"]
            if audio_inputs > 1:
                cmd += ["-filter_complex", "amix=inputs=2:duration=longest"]

        cmd += [str(out_path)]
        return cmd

    def start(self, width, height, fps, mic_device, system_audio, source_mode="Ekran", monitor_info=None, window_title=None):
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            raise RuntimeError(
                "FFmpeg bulunamadı. Lütfen FFmpeg'i kurun ve PATH'e ekleyin."
            )

        out_dir = get_output_dir()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_file = out_dir / f"Kayit_{timestamp}.mp4"

        cmd = self.build_command(width, height, fps, mic_device, system_audio, self.output_file, source_mode, monitor_info, window_title)

        self.log_file = out_dir / "ffmpeg_error.log"
        self._log_handle = open(self.log_file, "w", encoding="utf-8", errors="replace")

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=self._log_handle,
            **hidden_subprocess_kwargs(),
        )

        # FFmpeg ilk anda hata verip kapanmış mı kontrol et.
        time.sleep(1.0)
        if self.process.poll() is not None:
            try:
                self._log_handle.flush()
                self._log_handle.close()
            except Exception:
                pass
            try:
                error_text = self.log_file.read_text(encoding="utf-8", errors="replace").strip()
            except Exception:
                error_text = ""

            self.process = None
            if error_text:
                # Kullanıcıya aşırı uzun çıktı göstermeyelim.
                tail = error_text[-1800:]
                raise RuntimeError(
                    "FFmpeg kayıt başlatamadı.\n\n"
                    + tail
                    + f"\n\nHata günlüğü: {self.log_file}"
                )
            raise RuntimeError("FFmpeg kayıt başlatılamadan kapandı.")

        self.start_time = time.time()
        return self.output_file

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                if SYSTEM == "Windows":
                    # ffmpeg'e nazikçe 'q' göndererek dosyayı düzgün kapatmasını sağla
                    self.process.communicate(input=b"q", timeout=5)
                else:
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
        self.process = None
        try:
            if getattr(self, "_log_handle", None):
                self._log_handle.close()
                self._log_handle = None
        except Exception:
            pass

    def elapsed(self):
        if self.start_time:
            return int(time.time() - self.start_time)
        return 0


# --------------------------------------------------------------------------- #
#  Arayüz
# --------------------------------------------------------------------------- #

class ElitScreenRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_NAME)
        self.geometry("560x860")
        self.minsize(500, 760)
        self.configure(fg_color=BG_DARK)

        self.recorder = Recorder()
        self.is_recording = False
        self.timer_job = None

        self._build_ui()
        self._check_ffmpeg_banner()

    # ---------------------------------------------------------------- UI ---
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Başlık
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="🎬 Elite Screen Recorder",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFFFFF"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text=f"{platform.system()} • hafif & modern ekran kaydedici",
            font=ctk.CTkFont(size=12), text_color="#8A8A99"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Ana kart
        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=18)
        card.grid(row=1, column=0, sticky="nsew", padx=24, pady=10)
        card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        pad = {"padx": 20, "pady": (14, 4)}

        # Kayıt kaynağı
        ctk.CTkLabel(card, text="Kayıt Kaynağı", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", **pad
        )

        self.source_var = ctk.StringVar(value="Ekran")
        self.source_menu = ctk.CTkOptionMenu(
            card,
            values=["Ekran", "Pencere"],
            variable=self.source_var,
            command=self._on_source_changed,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38
        )
        self.source_menu.grid(row=1, column=0, sticky="ew", padx=20)

        # Monitör seçimi
        self.monitors = list_monitors()
        monitor_labels = [m[0] for m in self.monitors]
        self.monitor_var = ctk.StringVar(value=monitor_labels[0] if monitor_labels else "Tüm Masaüstü")
        self.monitor_menu = ctk.CTkOptionMenu(
            card,
            values=monitor_labels or ["Tüm Masaüstü"],
            variable=self.monitor_var,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38
        )
        self.monitor_menu.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 0))

        # Pencere seçimi
        self.window_var = ctk.StringVar(value="Pencere seçin")
        self.window_menu = ctk.CTkOptionMenu(
            card,
            values=["Pencere seçin"],
            variable=self.window_var,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38,
            state="disabled"
        )
        self.window_menu.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 0))

        self.refresh_windows_btn = ctk.CTkButton(
            card,
            text="↻ Pencereleri Yenile",
            height=30,
            corner_radius=8,
            fg_color="#232331", hover_color="#2E2E40",
            command=self._refresh_windows,
            state="disabled"
        )
        self.refresh_windows_btn.grid(row=4, column=0, sticky="ew", padx=20, pady=(8, 4))

        # Çözünürlük
        ctk.CTkLabel(card, text="Çözünürlük", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=5, column=0, sticky="w", **pad
        )
        self.res_var = ctk.StringVar(value="1080p (Full HD)")
        self.res_menu = ctk.CTkOptionMenu(
            card, values=list(RESOLUTIONS.keys()), variable=self.res_var,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38
        )
        self.res_menu.grid(row=6, column=0, sticky="ew", padx=20)

        # FPS
        ctk.CTkLabel(card, text="Kare Hızı (FPS)", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=7, column=0, sticky="w", **pad
        )
        self.fps_var = ctk.StringVar(value="30")
        self.fps_menu = ctk.CTkOptionMenu(
            card, values=FPS_OPTIONS, variable=self.fps_var,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38
        )
        self.fps_menu.grid(row=8, column=0, sticky="ew", padx=20)

        # Mikrofon
        ctk.CTkLabel(card, text="Mikrofon", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=9, column=0, sticky="w", **pad
        )
        self.mic_var = ctk.StringVar(value="Yok")
        self.mic_menu = ctk.CTkOptionMenu(
            card, values=list_microphones(), variable=self.mic_var,
            fg_color="#232331", button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=10, height=38
        )
        self.mic_menu.grid(row=10, column=0, sticky="ew", padx=20)

        self.refresh_mics_btn = ctk.CTkButton(
            card,
            text="↻ Mikrofonları Yenile",
            height=30,
            corner_radius=8,
            fg_color="#232331", hover_color="#2E2E40",
            command=self._refresh_microphones
        )
        self.refresh_mics_btn.grid(row=11, column=0, sticky="ew", padx=20, pady=(8, 0))

        # Sistem sesi
        self.sysaudio_var = ctk.BooleanVar(value=False)
        self.sysaudio_check = ctk.CTkCheckBox(
            card, text="Sistem sesini de kaydet (Stereo Mix / Pulse gerektirir)",
            variable=self.sysaudio_var, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(size=12)
        )
        self.sysaudio_check.grid(row=12, column=0, sticky="w", padx=20, pady=(16, 4))

        # Çıktı klasörü
        out_frame = ctk.CTkFrame(card, fg_color="transparent")
        out_frame.grid(row=13, column=0, sticky="ew", padx=20, pady=(16, 6))
        out_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(out_frame, text="Çıktı klasörü", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.output_dir = get_output_dir()
        self.out_label = ctk.CTkLabel(
            out_frame, text=str(self.output_dir), font=ctk.CTkFont(size=11),
            text_color="#8A8A99", wraplength=380, justify="left"
        )
        self.out_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        ctk.CTkButton(
            out_frame, text="📂 Klasörü Aç", width=110, height=30, corner_radius=8,
            fg_color="#232331", hover_color="#2E2E40", text_color="#FFFFFF",
            command=self._open_output_folder
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        # Durum ve süre
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(4, 0))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame, text="Hazır", font=ctk.CTkFont(size=13),
            text_color="#8A8A99"
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.timer_label = ctk.CTkLabel(
            status_frame, text="00:00:00", font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT
        )
        self.timer_label.grid(row=0, column=1, sticky="e")

        # Başlat / Durdur butonu
        self.record_btn = ctk.CTkButton(
            self, text="● Kaydı Başlat", height=54, corner_radius=16,
            font=ctk.CTkFont(size=17, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self._toggle_recording
        )
        self.record_btn.grid(row=3, column=0, sticky="ew", padx=24, pady=(14, 24))

    def _check_ffmpeg_banner(self):
        if not find_ffmpeg():
            self.status_label.configure(
                text="⚠ FFmpeg bulunamadı — lütfen kurun ve PATH'e ekleyin",
                text_color=ACCENT_DANGER
            )

    # ------------------------------------------------------------ Actions ---
    def _refresh_microphones(self):
        microphones = list_microphones()
        self.mic_menu.configure(values=microphones)

        current = self.mic_var.get()
        if current not in microphones:
            self.mic_var.set(microphones[0] if microphones else "Yok")

    def _on_source_changed(self, value):
        if value == "Pencere":
            self.monitor_menu.configure(state="disabled")
            self.window_menu.configure(state="normal")
            self.refresh_windows_btn.configure(state="normal")
            self._refresh_windows()
        else:
            self.monitor_menu.configure(state="normal")
            self.window_menu.configure(state="disabled")
            self.refresh_windows_btn.configure(state="disabled")

    def _refresh_windows(self):
        windows = list_windows()
        if not windows:
            windows = ["Açık pencere bulunamadı"]
        self.window_menu.configure(values=windows)
        self.window_var.set(windows[0])

    def _get_selected_monitor(self):
        selected = self.monitor_var.get()
        for info in self.monitors:
            if info[0] == selected:
                return info
        return None

    def _open_output_folder(self):
        path = str(self.output_dir)
        try:
            if SYSTEM == "Windows":
                os.startfile(path)
            elif SYSTEM == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Klasör açılamadı:\n{e}")

    def _toggle_recording(self):
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        if not find_ffmpeg():
            messagebox.showerror(
                APP_NAME,
                "FFmpeg bulunamadı. Lütfen FFmpeg'i kurup PATH'e ekleyin, sonra tekrar deneyin."
            )
            return

        width, height = RESOLUTIONS[self.res_var.get()]
        fps = self.fps_var.get()
        mic = self.mic_var.get()
        sys_audio = self.sysaudio_var.get()

        source_mode = self.source_var.get()
        monitor_info = self._get_selected_monitor() if source_mode == "Ekran" else None
        window_title = self.window_var.get() if source_mode == "Pencere" else None

        if source_mode == "Pencere" and (not window_title or window_title in ("Pencere seçin", "Açık pencere bulunamadı")):
            messagebox.showerror(APP_NAME, "Lütfen kaydedilecek pencereyi seçin.")
            return

        def worker():
            try:
                out_file = self.recorder.start(
                    width, height, fps, mic, sys_audio,
                    source_mode, monitor_info, window_title
                )
                self.is_recording = True
                self.after(0, self._on_record_started, out_file)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(APP_NAME, str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_record_started(self, out_file):
        self.record_btn.configure(
            text="■ Kaydı Durdur", fg_color=ACCENT_DANGER, hover_color=ACCENT_DANGER_HOVER
        )
        self.status_label.configure(text=f"Kaydediliyor → {out_file.name}", text_color="#4CD97B")
        self._tick_timer()

    def _stop_recording(self):
        self.status_label.configure(text="Kayıt kaydediliyor / kapatılıyor...", text_color="#8A8A99")
        self.record_btn.configure(state="disabled")

        def worker():
            self.recorder.stop()
            self.is_recording = False
            self.after(0, self._on_record_stopped)

        threading.Thread(target=worker, daemon=True).start()

    def _on_record_stopped(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_label.configure(text="00:00:00")
        self.record_btn.configure(
            text="● Kaydı Başlat", fg_color=ACCENT, hover_color=ACCENT_HOVER, state="normal"
        )
        self.status_label.configure(
            text=f"Kayıt kaydedildi: {self.recorder.output_file}", text_color="#4CD97B"
        )

    def _tick_timer(self):
        if self.is_recording:
            secs = self.recorder.elapsed()
            h, rem = divmod(secs, 3600)
            m, s = divmod(rem, 60)
            self.timer_label.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
            self.timer_job = self.after(1000, self._tick_timer)

    def on_close(self):
        if self.is_recording:
            self.recorder.stop()
        self.destroy()


def main():
    ensure_admin_on_windows()
    app = ElitScreenRecorderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
