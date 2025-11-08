
#!/usr/bin/env python3
"""
PulseDownloader.py
Version: 0.0.24Ud8Vo
- Direct-file downloader (requests + streaming + resume support via Range header if supported)
- Optional yt-dlp fallback (if you have yt-dlp installed)
- WARNING: Only download content you have permission to download.
"""

__version__ = "0.0.24Ud8Vo"

import os
import sys
import threading
import subprocess
import shutil
from urllib.parse import urlparse, urlunparse
import re
import requests
from tqdm import tqdm
import logging
import argparse

CHUNK_SIZE = 1024 * 1024  # 1 MiB
TIMEOUT = 15

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("downloader.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PulseDownloader")


# ---------- Sanitization Helpers ----------
def sanitize_url(url: str) -> str:
    """Sanitize and validate a URL."""
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid URL provided.")
    # Remove dangerous characters from path/query
    safe_path = re.sub(r'[^\w\-./]', '', parsed.path)
    safe_query = re.sub(r'[^\w\-=&]', '', parsed.query)
    sanitized = urlunparse((parsed.scheme, parsed.netloc, safe_path, '', safe_query, ''))
    return sanitized

def sanitize_path(path: str) -> str:
    """Sanitize a filesystem path (folder or filename)."""
    # Remove dangerous characters, allow only safe ones
    safe = re.sub(r'[<>:"/\\|?*]', '', path)
    safe = safe.strip()
    return safe

def is_direct_media_url(url: str) -> bool:
    """Check if the URL points to a direct media file by extension."""
    media_exts = ('.mp4', '.mkv', '.webm', '.mov', '.flv', '.avi', '.ts', '.m4v')
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in media_exts)

def safe_filename_from_url(url: str) -> str:
    """Extract a safe filename from the URL and sanitize it."""
    path = urlparse(url).path
    name = os.path.basename(path) or "downloaded_video"
    return sanitize_path(name)

def direct_download(url: str, out_path: str) -> str:
    """
    Stream-download a direct file URL using requests with a progress bar and resume support.
    """
    headers = {}
    resume_pos = 0
    if os.path.exists(out_path):
        resume_pos = os.path.getsize(out_path)
        if resume_pos > 0:
            headers['Range'] = f'bytes={resume_pos}-'
    try:
        url = sanitize_url(url)
        out_path = sanitize_path(out_path)
        with requests.get(url, stream=True, timeout=TIMEOUT, headers=headers) as r:
            r.raise_for_status()
            total = None
            if 'Content-Range' in r.headers:
                content_range = r.headers['Content-Range']
                try:
                    total = int(content_range.split('/')[-1])
                except Exception:
                    total = None
            elif 'Content-Length' in r.headers:
                total = int(r.headers['Content-Length']) + resume_pos
            mode = 'ab' if resume_pos else 'wb'
            with open(out_path, mode) as f, tqdm(total=total, unit='B', unit_scale=True, desc=os.path.basename(out_path), initial=resume_pos) as pbar:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue
                    f.write(chunk)
                    pbar.update(len(chunk))
        logger.info(f"Download complete: {out_path}")
        return out_path
    except Exception as e:
        logger.error(f"Direct download failed: {e}")
        raise


def yt_dlp_download(url: str, out_dir: str) -> bool:
    """
    Use yt-dlp if available. Looks for yt-dlp.exe in the _internal folder next to the executable, then falls back to PATH.
    """
    import sys
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    internal_yt_dlp = os.path.join(exe_dir, "yt-dlp", "yt-dlp.exe")
    yt_dlp_exe = internal_yt_dlp if os.path.exists(internal_yt_dlp) else shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if not yt_dlp_exe:
        logger.error("yt-dlp not found in _internal folder or on PATH. Please ensure yt-dlp.exe is present.")
        raise FileNotFoundError("yt-dlp not found in _internal folder or on PATH. Please ensure yt-dlp.exe is present.")
    url = sanitize_url(url)
    out_dir = os.path.abspath(sanitize_path(out_dir))
    # Ensure output directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    cmd = [yt_dlp_exe, "-f", "best", "-o", os.path.join(out_dir, "%(title)s.%(ext)s"), url]
    print(f"[yt-dlp] Command: {' '.join(cmd)}")
    print(f"[yt-dlp] Output directory: {out_dir}")
    logger.info(f"[yt-dlp] Command: {' '.join(cmd)}")
    logger.info(f"[yt-dlp] Output directory: {out_dir}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(f"yt-dlp STDOUT:\n{proc.stdout}")
    print(f"yt-dlp STDERR:\n{proc.stderr}")
    logger.info(f"yt-dlp STDOUT:\n{proc.stdout}")
    logger.info(f"yt-dlp STDERR:\n{proc.stderr}")
    if proc.returncode != 0:
        error_msg = f"yt-dlp failed with exit code {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        logger.error(error_msg)
        with open("downloader.log", "a", encoding="utf-8") as logf:
            logf.write(error_msg + "\n")
        raise RuntimeError(error_msg)
    logger.info(f"yt-dlp finished.")
    return True

def download_main(url: str, out_dir: str = ".", auto_fallback: bool = False, no_prompt: bool = False) -> str:
    """
    Main download logic for CLI. Tries direct download, falls back to yt-dlp if needed.
    """
    logger.info("Reminder: Only download content you have permission to download. Respect copyright and site Terms of Service.")
    url = sanitize_url(url)
    out_dir = sanitize_path(out_dir)
    try_direct = is_direct_media_url(url)
    filename = safe_filename_from_url(url)
    out_path = os.path.join(out_dir, filename)
    if try_direct:
        logger.info(f"Detected direct media file URL. Downloading to: {out_path}")
        try:
            direct_download(url, out_path)
            return out_path
        except Exception as e:
            logger.warning(f"Direct download failed: {e}")
            logger.info("Trying yt-dlp fallback (if installed)...")
            # If direct download fails, fall back to yt-dlp
            try:
                yt_dlp_download(url, out_dir)
                return out_dir
            except Exception as e2:
                logger.error(f"yt-dlp error: {e2}")
                return None
    else:
        # Not a direct media file, use yt-dlp automatically
        logger.info("Using yt-dlp for non-direct media URL...")
        try:
            yt_dlp_download(url, out_dir)
            return out_dir
        except Exception as e:
            logger.error(f"yt-dlp error: {e}")
            return None

# ---------- Optional simple GUI ----------
def run_gui():
    import sys
    import os
    from PyQt5 import QtWidgets, QtCore, QtGui
    class DownloaderWindow(QtWidgets.QWidget):
        def is_supported_platform(self, url):
            # List of major platforms supported by yt-dlp (from yt-dlp repo)
            yt_dlp_domains = [
                "youtube.com", "youtu.be", "soundcloud.com", "vimeo.com", "dailymotion.com", "dai.ly", "facebook.com", "fb.watch", "twitter.com", "x.com", "tiktok.com", "instagram.com", "bandcamp.com", "twitch.tv", "bilibili.com", "reddit.com", "nicovideo.jp", "vk.com", "tumblr.com", "mixcloud.com", "archive.org", "ted.com", "peertube", "rumble.com", "odyssey.com", "odysee.com", "kick.com", "streamable.com", "liveleak.com", "metacafe.com", "pornhub.com", "xvideos.com", "xhamster.com", "adultswim.com", "funimation.com", "crunchyroll.com", "animeflv.net", "animeid.tv", "anime-planet.com", "9anime.to", "bitchute.com", "lbry.tv", "lbry.com", "odysee.com", "mediaset.it", "rai.it", "zdf.de", "ard.de", "prosieben.de", "sat1.de", "joyn.de", "myspass.de", "vevo.com", "cbc.ca", "cbs.com", "nbc.com", "abc.com", "fox.com", "pbs.org", "pluto.tv", "paramountplus.com", "disneyplus.com", "hulu.com", "netflix.com", "primevideo.com", "amazon.com", "apple.com", "hbomax.com", "hbogo.com", "starz.com", "showtime.com", "crackle.com", "popcornflix.com", "filmrise.com", "tubi.tv", "plex.tv", "fubo.tv", "sling.com", "sling.tv", "espn.com", "espnplus.com", "nba.com", "mlb.com", "nhl.com", "nfl.com", "wwe.com", "ufc.com", "dazn.com", "sky.com", "bbc.co.uk", "itv.com", "channel4.com", "channel5.com", "my5.tv", "stv.tv", "rtve.es", "rt.com", "euronews.com", "aljazeera.com", "cnn.com", "msnbc.com", "cnbc.com", "bloomberg.com", "reuters.com", "vice.com", "vice.tv", "forbes.com", "businessinsider.com", "theguardian.com", "nytimes.com", "washingtonpost.com", "wsj.com", "latimes.com", "usatoday.com", "news.com.au", "news24.com", "newsnow.co.uk", "news.sky.com", "news.yahoo.com", "yahoo.com", "yahoo.co.jp", "yahoo.co.uk", "yahoo.de", "yahoo.fr", "yahoo.it", "yahoo.es", "yahoo.ca", "yahoo.com.au", "yahoo.com.sg", "yahoo.com.hk", "yahoo.com.tw", "yahoo.com.ph", "yahoo.com.my", "yahoo.com.in", "yahoo.com.id", "yahoo.com.vn", "yahoo.com.th", "yahoo.com.br", "yahoo.com.mx", "yahoo.com.ar", "yahoo.com.cl", "yahoo.com.co", "yahoo.com.pe", "yahoo.com.ve", "yahoo.com.ec", "yahoo.com.uy", "yahoo.com.py", "yahoo.com.bo", "yahoo.com.cr", "yahoo.com.pa", "yahoo.com.gt", "yahoo.com.hn", "yahoo.com.ni", "yahoo.com.sv", "yahoo.com.do", "yahoo.com.cu", "yahoo.com.pr", "yahoo.com.jm", "yahoo.com.tt", "yahoo.com.bb", "yahoo.com.bs", "yahoo.com.ag", "yahoo.com.bz", "yahoo.com.dm", "yahoo.com.gd", "yahoo.com.kn", "yahoo.com.lc", "yahoo.com.ms", "yahoo.com.vc", "yahoo.com.sr", "yahoo.com.gy", "yahoo.com.su", "yahoo.com.kz", "yahoo.com.ua", "yahoo.com.by", "yahoo.com.md", "yahoo.com.ge", "yahoo.com.am", "yahoo.com.az", "yahoo.com.tr", "yahoo.com.il", "yahoo.com.ps", "yahoo.com.lb", "yahoo.com.sy", "yahoo.com.jo", "yahoo.com.iq", "yahoo.com.kw", "yahoo.com.sa", "yahoo.com.om", "yahoo.com.ae", "yahoo.com.qa", "yahoo.com.bh", "yahoo.com.eg", "yahoo.com.ma", "yahoo.com.tn", "yahoo.com.dz", "yahoo.com.ly", "yahoo.com.sd", "yahoo.com.ss", "yahoo.com.et", "yahoo.com.ke", "yahoo.com.ug", "yahoo.com.tz", "yahoo.com.rw", "yahoo.com.bi", "yahoo.com.mw", "yahoo.com.zm", "yahoo.com.zw", "yahoo.com.na", "yahoo.com.bw", "yahoo.com.ls", "yahoo.com.sz", "yahoo.com.mg", "yahoo.com.mu", "yahoo.com.sc", "yahoo.com.cv", "yahoo.com.sn", "yahoo.com.ml", "yahoo.com.gn", "yahoo.com.ci", "yahoo.com.bf", "yahoo.com.ne", "yahoo.com.tg", "yahoo.com.bj", "yahoo.com.sl", "yahoo.com.lr", "yahoo.com.gh", "yahoo.com.ng", "yahoo.com.cm", "yahoo.com.ga", "yahoo.com.cg", "yahoo.com.cd", "yahoo.com.ao", "yahoo.com.mz", "yahoo.com.sz", "yahoo.com.er", "yahoo.com.dj", "yahoo.com.so", "yahoo.com.sd", "yahoo.com.ss", "yahoo.com.et", "yahoo.com.ke", "yahoo.com.ug", "yahoo.com.tz", "yahoo.com.rw", "yahoo.com.bi", "yahoo.com.mw", "yahoo.com.zm", "yahoo.com.zw", "yahoo.com.na", "yahoo.com.bw", "yahoo.com.ls", "yahoo.com.sz", "yahoo.com.mg", "yahoo.com.mu", "yahoo.com.sc", "yahoo.com.cv", "yahoo.com.sn", "yahoo.com.ml", "yahoo.com.gn", "yahoo.com.ci", "yahoo.com.bf", "yahoo.com.ne", "yahoo.com.tg", "yahoo.com.bj", "yahoo.com.sl", "yahoo.com.lr", "yahoo.com.gh", "yahoo.com.ng", "yahoo.com.cm", "yahoo.com.ga", "yahoo.com.cg", "yahoo.com.cd", "yahoo.com.ao", "yahoo.com.mz", "yahoo.com.sz", "yahoo.com.er", "yahoo.com.dj", "yahoo.com.so", "yahoo.com.sd", "yahoo.com.ss", "yahoo.com.et", "yahoo.com.ke", "yahoo.com.ug", "yahoo.com.tz", "yahoo.com.rw", "yahoo.com.bi", "yahoo.com.mw", "yahoo.com.zm", "yahoo.com.zw", "yahoo.com.na", "yahoo.com.bw", "yahoo.com.ls", "yahoo.com.sz", "yahoo.com.mg", "yahoo.com.mu", "yahoo.com.sc", "yahoo.com.cv"
            ]
            url_l = url.lower()
            return any(domain in url_l for domain in yt_dlp_domains)
        def setup_tray_icon(self):
            self.tray_icon = QtWidgets.QSystemTrayIcon(self)
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("Video Downloader is running")

            tray_menu = QtWidgets.QMenu()
            restore_action = tray_menu.addAction("Restore")
            exit_action = tray_menu.addAction("Exit")
            restore_action.triggered.connect(self.showNormal)
            exit_action.triggered.connect(QtWidgets.qApp.quit)
            self.tray_icon.setContextMenu(tray_menu)

            self.tray_icon.activated.connect(self.on_tray_activated)

        def on_tray_activated(self, reason):
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                self.showNormal()
                self.raise_()
                self.activateWindow()

        def changeEvent(self, event):
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    QtCore.QTimer.singleShot(0, self.hide)
                    self.tray_icon.show()
                elif self.isVisible():
                    self.tray_icon.hide()
            super().changeEvent(event)

        def closeEvent(self, event):
            self.tray_icon.hide()
            event.accept()
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"PulseDownloader v{__version__}")
            self.resize(700, 300)
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(18)

            form_layout = QtWidgets.QFormLayout()
            form_layout.setHorizontalSpacing(18)
            form_layout.setVerticalSpacing(16)

            label_font = QtGui.QFont("Segoe UI", 13)
            input_font = QtGui.QFont("Segoe UI", 12)
            button_font = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold)
            status_font = QtGui.QFont("Segoe UI", 11, QtGui.QFont.StyleItalic)

            url_label = QtWidgets.QLabel("Video URL:")
            url_label.setFont(label_font)
            self.url_edit = QtWidgets.QLineEdit()
            self.url_edit.setPlaceholderText("Enter video URL...")
            self.url_edit.setFont(input_font)
            form_layout.addRow(url_label, self.url_edit)

            folder_label = QtWidgets.QLabel("Save folder:")
            folder_label.setFont(label_font)
            self.folder_edit = QtWidgets.QLineEdit(os.getcwd())
            self.folder_edit.setFont(input_font)
            self.folder_btn = QtWidgets.QPushButton("Browse")
            self.folder_btn.setFont(button_font)
            folder_layout = QtWidgets.QHBoxLayout()
            folder_layout.addWidget(self.folder_edit)
            folder_layout.addWidget(self.folder_btn)
            form_layout.addRow(folder_label, folder_layout)

            main_layout.addLayout(form_layout)

            self.download_btn = QtWidgets.QPushButton("Download Video")
            self.download_btn.setFont(button_font)
            self.download_btn.setMinimumHeight(40)
            self.download_btn.setStyleSheet("background-color: #0078d7; color: white; border-radius: 6px;")
            main_layout.addWidget(self.download_btn)

            self.music_btn = QtWidgets.QPushButton("Download Music (MP3)")
            self.music_btn.setFont(button_font)
            self.music_btn.setMinimumHeight(40)
            self.music_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 6px;")
            main_layout.addWidget(self.music_btn)

            self.status = QtWidgets.QLabel("Ready")
            self.status.setFont(status_font)
            self.status.setStyleSheet("color: #222; font-style: italic;")
            main_layout.addWidget(self.status)

            self.timer_label = QtWidgets.QLabel("Elapsed: 00:00")
            self.timer_label.setFont(status_font)
            self.timer_label.setStyleSheet("color: #0078d7; font-style: italic;")
            main_layout.addWidget(self.timer_label)

            footer = QtWidgets.QLabel("Only download content you have permission to download.")
            bold_footer_font = QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold)
            bold_footer_font.setItalic(True)
            footer.setFont(bold_footer_font)
            footer.setStyleSheet("color: purple; font-size: 13pt; font-style: italic; font-weight: bold;")
            main_layout.addWidget(footer)

            self.folder_btn.clicked.connect(self.pick_folder)
            self.download_btn.clicked.connect(self.download_video)
            self.music_btn.clicked.connect(self.download_music)

            self.exit_btn = QtWidgets.QPushButton("Exit")
            self.exit_btn.setFont(button_font)
            self.exit_btn.setMinimumHeight(32)
            self.exit_btn.setStyleSheet("background-color: #dc3545; color: white; border-radius: 6px;")
            main_layout.addWidget(self.exit_btn)
            self.exit_btn.clicked.connect(self.close)

            # Timer setup
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_timer)
            self.elapsed_seconds = 0

            # Tray icon setup
            self.setup_tray_icon()

        def pick_folder(self):
            d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", self.folder_edit.text())
            if d:
                self.folder_edit.setText(d)

        def set_status(self, msg, color="#222"):
            self.status.setText(msg)
            self.status.setStyleSheet(f"color: {color}; font-style: italic;")

        def start_timer(self):
            self.elapsed_seconds = 0
            self.timer.start(1000)
            self.update_timer()

        def stop_timer(self):
            self.timer.stop()
            self.elapsed_seconds = 0
            self.update_timer()

        def update_timer(self):
            mins, secs = divmod(self.elapsed_seconds, 60)
            self.timer_label.setText(f"Elapsed: {mins:02d}:{secs:02d}")
            if self.timer.isActive():
                self.elapsed_seconds += 1

        def download_video(self):
            url = self.url_edit.text().strip()
            base_dir = self.folder_edit.text().strip()
            video_dir = os.path.join(base_dir, "OS-Videos")
            if not os.path.exists(video_dir):
                os.makedirs(video_dir, exist_ok=True)
            if not url:
                self.set_status("Enter a URL", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "Please enter a video URL.")
                self.stop_timer()
                return
            if self.is_supported_platform(url) and not shutil.which("yt-dlp"):
                self.set_status("This platform requires yt-dlp. Please install yt-dlp.", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "This platform requires yt-dlp. Please install yt-dlp.")
                self.stop_timer()
                return
            self.set_status("Downloading Video...", "#0078d7")
            self.start_timer()
            # Always use yt-dlp for supported platforms
            cmd = ["yt-dlp", url] if self.is_supported_platform(url) else ["yt-dlp", url]
            try:
                subprocess.run(cmd, cwd=video_dir, check=True)
                self.set_status(f"Download complete! Saved in OS-Videos", "#28a745")
                QtWidgets.QMessageBox.information(self, "Success", f"Download complete! Saved in OS-Videos folder.")
            except subprocess.CalledProcessError:
                self.set_status("An error occurred during download.", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "An error occurred during download.")
            finally:
                self.stop_timer()

        def download_music(self):
            url = self.url_edit.text().strip()
            base_dir = self.folder_edit.text().strip()
            music_dir = os.path.join(base_dir, "OS-Music")
            if not os.path.exists(music_dir):
                os.makedirs(music_dir, exist_ok=True)
            if not url:
                self.set_status("Enter a URL", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "Please enter a video URL.")
                self.stop_timer()
                return
            if self.is_supported_platform(url) and not shutil.which("yt-dlp"):
                self.set_status("This platform requires yt-dlp. Please install yt-dlp.", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "This platform requires yt-dlp. Please install yt-dlp.")
                self.stop_timer()
                return
            self.set_status("Downloading Music...", "#4CAF50")
            self.start_timer()
            # Always use yt-dlp for supported platforms
            if self.is_supported_platform(url):
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", url]
            else:
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "-f", "ba[acodec^=mp3]/ba/b", url]
            try:
                subprocess.run(cmd, cwd=music_dir, check=True)
                self.set_status(f"Download complete! Saved in OS-Music", "#28a745")
                QtWidgets.QMessageBox.information(self, "Success", f"Download complete! Saved in OS-Music folder.")
            except subprocess.CalledProcessError:
                self.set_status("An error occurred during download.", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "An error occurred during download.")
            finally:
                self.stop_timer()
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(18)

            form_layout = QtWidgets.QFormLayout()
            form_layout.setHorizontalSpacing(18)
            form_layout.setVerticalSpacing(16)

            label_font = QtGui.QFont("Segoe UI", 13)
            input_font = QtGui.QFont("Segoe UI", 12)
            button_font = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold)
            status_font = QtGui.QFont("Segoe UI", 11, QtGui.QFont.StyleItalic)

            url_label = QtWidgets.QLabel("Video URL:")
            url_label.setFont(label_font)
            self.url_edit = QtWidgets.QLineEdit()
            self.url_edit.setPlaceholderText("Enter video URL...")
            self.url_edit.setFont(input_font)
            form_layout.addRow(url_label, self.url_edit)

            folder_label = QtWidgets.QLabel("Save folder:")
            folder_label.setFont(label_font)
            self.folder_edit = QtWidgets.QLineEdit(os.getcwd())
            self.folder_edit.setFont(input_font)
            self.folder_btn = QtWidgets.QPushButton("Browse")
            self.folder_btn.setFont(button_font)
            folder_layout = QtWidgets.QHBoxLayout()
            folder_layout.addWidget(self.folder_edit)
            folder_layout.addWidget(self.folder_btn)
            form_layout.addRow(folder_label, folder_layout)

            main_layout.addLayout(form_layout)

            self.download_btn = QtWidgets.QPushButton("Download Video")
            self.download_btn.setFont(button_font)
            self.download_btn.setMinimumHeight(40)
            self.download_btn.setStyleSheet("background-color: #0078d7; color: white; border-radius: 6px;")
            main_layout.addWidget(self.download_btn)

            self.music_btn = QtWidgets.QPushButton("Download Music (MP3)")
            self.music_btn.setFont(button_font)
            self.music_btn.setMinimumHeight(40)
            self.music_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 6px;")
            main_layout.addWidget(self.music_btn)

            self.status = QtWidgets.QLabel("Ready")
            self.status.setFont(status_font)
            self.status.setStyleSheet("color: #222; font-style: italic;")
            main_layout.addWidget(self.status)

            self.timer_label = QtWidgets.QLabel("Elapsed: 00:00")
            self.timer_label.setFont(status_font)
            self.timer_label.setStyleSheet("color: #0078d7; font-style: italic;")
            main_layout.addWidget(self.timer_label)

            footer = QtWidgets.QLabel("Only download content you have permission to download.")
            bold_footer_font = QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold)
            bold_footer_font.setItalic(True)
            footer.setFont(bold_footer_font)
            footer.setStyleSheet("color: purple; font-size: 13pt; font-style: italic; font-weight: bold;")
            main_layout.addWidget(footer)

            self.folder_btn.clicked.connect(self.pick_folder)
            self.download_btn.clicked.connect(self.download_video)
            self.music_btn.clicked.connect(self.download_music)

            self.exit_btn = QtWidgets.QPushButton("Exit")
            self.exit_btn.setFont(button_font)
            self.exit_btn.setMinimumHeight(32)
            self.exit_btn.setStyleSheet("background-color: #dc3545; color: white; border-radius: 6px;")
            main_layout.addWidget(self.exit_btn)
            self.exit_btn.clicked.connect(self.close)

            # Timer setup
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_timer)
            self.elapsed_seconds = 0

        def on_tray_activated(self, reason):
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                self.showNormal()
                self.raise_()
                self.activateWindow()

        def changeEvent(self, event):
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    QtCore.QTimer.singleShot(0, self.hide)
                    self.tray_icon.show()
                elif self.isVisible():
                    self.tray_icon.hide()
            super().changeEvent(event)

        # closeEvent removed (no tray icon logic)

        def pick_folder(self):
            d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", self.folder_edit.text())
            if d:
                self.folder_edit.setText(sanitize_path(d))

        def set_status(self, msg, color="#222"): 
            self.status.setText(msg)
            self.status.setStyleSheet(f"color: {color}; font-style: italic;")
            # Only show pop-up for errors or completion, not for every update
            if color == "#dc3545" or color == "#28a745":
                QtWidgets.QMessageBox.information(self, "Status", msg)

        def start_download(self):
            url = self.url_edit.text().strip()
            out_dir = self.folder_edit.text().strip()
            self.progress.setValue(0)
            try:
                url = sanitize_url(url)
                out_dir = sanitize_path(out_dir)
            except Exception as e:
                self.set_status(f"Input error: {e}", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", f"Input error: {e}")
                return
            if not url:
                self.set_status("Enter a URL", "#dc3545")
                QtWidgets.QMessageBox.critical(self, "Error", "Enter a URL")
                return
            self.set_status("Checking URL...", "#0078d7")
            self.thread = QtCore.QThread()
            worker = DownloadWorker(url, out_dir)
            worker.moveToThread(self.thread)
            worker.progress.connect(self.progress.setValue)
            worker.status.connect(self.set_status)
            worker.finished.connect(lambda msg: QtWidgets.QMessageBox.information(self, "Done", msg))
            worker.error.connect(lambda msg: QtWidgets.QMessageBox.critical(self, "Error", msg))
            self.thread.started.connect(worker.run)
            worker.finished.connect(self.thread.quit)
            worker.finished.connect(worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    class DownloadWorker(QtCore.QObject):
        progress = QtCore.pyqtSignal(int)
        status = QtCore.pyqtSignal(str, str)
        finished = QtCore.pyqtSignal(str)
        error = QtCore.pyqtSignal(str)

        def __init__(self, url, out_dir):
            super().__init__()
            self.url = sanitize_url(url)
            self.out_dir = sanitize_path(out_dir)

        def run(self):
            try:
                if is_direct_media_url(self.url):
                    name = safe_filename_from_url(self.url)
                    out_path = os.path.join(self.out_dir, name)
                    self.status.emit(f"Downloading {name}...", "#0078d7")
                    from tqdm import tqdm as tqdm_orig
                    worker = self
                    class TqdmQt(tqdm_orig):
                        def update(self, n=1):
                            super().update(n)
                            percent = int(self.n / (self.total or 1) * 100) if self.total else 0
                            worker.progress.emit(percent)
                    import builtins
                    builtins.tqdm = TqdmQt
                    try:
                        direct_download(self.url, out_path)
                        builtins.tqdm = tqdm_orig
                        self.progress.emit(100)
                        self.status.emit(f"Saved: {out_path}", "#28a745")
                        self.finished.emit(f"Saved: {out_path}")
                    except Exception as e:
                        self.status.emit("Direct download failed. Trying yt-dlp...", "#dc3545")
                        # Try yt-dlp fallback
                        if not shutil.which("yt-dlp"):
                            self.status.emit("yt-dlp missing", "#dc3545")
                            self.error.emit("yt-dlp is not installed. Install with: pip install yt-dlp")
                            builtins.tqdm = tqdm_orig
                            return
                        try:
                            self.status.emit("Running yt-dlp...", "#0078d7")
                            yt_dlp_download(self.url, self.out_dir)
                            self.progress.emit(100)
                            self.status.emit("yt-dlp finished", "#28a745")
                            self.finished.emit("yt-dlp finished")
                        except Exception as e2:
                            self.status.emit("yt-dlp failed", "#dc3545")
                            # Show full error details in pop-up
                            self.error.emit(f"yt-dlp error: {e2}")
                            # Also write to log file
                            with open("downloader.log", "a", encoding="utf-8") as logf:
                                logf.write(f"yt-dlp error: {e2}\n")
                        builtins.tqdm = tqdm_orig
                        return
                else:
                    if not shutil.which("yt-dlp"):
                        self.status.emit("yt-dlp missing", "#dc3545")
                        self.error.emit("yt-dlp is not installed. Install with: pip install yt-dlp")
                        return
                    try:
                        self.status.emit("Running yt-dlp...", "#0078d7")
                        yt_dlp_download(self.url, self.out_dir)
                        self.progress.emit(100)
                        self.status.emit("yt-dlp finished", "#28a745")
                        self.finished.emit("yt-dlp finished")
                    except Exception as e:
                        self.status.emit("yt-dlp failed", "#dc3545")
                        # Show full error details in pop-up
                        self.error.emit(f"yt-dlp error: {e}")
                        # Also write to log file
                        with open("downloader.log", "a", encoding="utf-8") as logf:
                            logf.write(f"yt-dlp error: {e}\n")
            except Exception as e:
                self.status.emit("Error", "#dc3545")
                self.error.emit(str(e))
                # Also write to log file
                with open("downloader.log", "a", encoding="utf-8") as logf:
                    logf.write(f"General error: {e}\n")

    app = QtWidgets.QApplication(sys.argv)
    win = DownloaderWindow()
    win.show()
    app.exec_()

# ---------- CLI Argument Parsing ----------
def main():
    parser = argparse.ArgumentParser(
        description="Professional Video Downloader (direct file or yt-dlp fallback)"
    )
    parser.add_argument("url", nargs="?", help="Video URL to download")
    parser.add_argument("-o", "--out-dir", default=".", help="Output directory")
    parser.add_argument("--no-gui", action="store_true", help="Do not launch GUI, use CLI only")
    parser.add_argument("--auto-fallback", action="store_true", help="Automatically use yt-dlp fallback if direct download fails")
    parser.add_argument("--no-prompt", action="store_true", help="Do not prompt for yt-dlp fallback (for automation)")
    args = parser.parse_args()

    if not args.url:
        if args.no_gui:
            logger.error("No URL provided. Usage: python video_downloader.py <url> [-o OUT_DIR]")
            sys.exit(1)
        # launch GUI by default
        try:
            run_gui()
        except Exception as e:
            logger.error(f"Failed to start GUI: {e}")
            print("You can use CLI: python video_downloader.py <url> [-o OUT_DIR]")
        finally:
            sys.exit(0)
    # CLI mode
    try:
        url = sanitize_url(args.url)
        out_dir = sanitize_path(args.out_dir)
    except Exception as e:
        logger.error(f"Input error: {e}")
        sys.exit(1)
    download_main(
        url,
        out_dir=out_dir,
        auto_fallback=args.auto_fallback,
        no_prompt=args.no_prompt
    )

# ---------- Entry point ----------
if __name__ == "__main__":
    run_gui()
